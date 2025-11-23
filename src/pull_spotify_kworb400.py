# src/pull_spotify_kworb400.py
# reads data/kworb_top_400.csv (columns: Artist, Title)
# gets a Spotify access token using client credentials from .env
# searches each song on Spotify and saves basic track metadata
# fetches artist followers/popularity/genres per song
# saves to data/spotify_from_kworb_400.csv

import time
import base64
import requests
import pandas as pd
import argparse
from pathlib import Path
from src.config import (data_folder,kworb_output_filename,spotify_from_kworb_filename,sleep_between_calls,checkpoint_every,get_artist_stats,spotify_token_url,spotify_search_url,spotify_artists_url,spotify_client_id,spotify_client_secret,)

data_folder.mkdir(parents=True, exist_ok=True)

default_kworb_file = data_folder / kworb_output_filename
default_out_file = data_folder / spotify_from_kworb_filename

token_url = spotify_token_url
search_url = spotify_search_url
artists_url = spotify_artists_url

client_id = spotify_client_id
client_secret = spotify_client_secret

def get_access_token():
    if not client_id or not client_secret:
        raise RuntimeError("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env")

    auth_string = f"{client_id}:{client_secret}".encode("utf-8")
    base64_auth = base64.b64encode(auth_string).decode("utf-8")

    response = requests.post(token_url,headers={"Authorization": f"Basic {base64_auth}"},data={"grant_type": "client_credentials"},timeout=30,)
    response.raise_for_status()
    data = response.json()
    return data["access_token"]

def normalize_text(value):
    if value:
        return str(value).strip().lower()
    else:
        return ""


def search_track_first(query, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": query, "type": "track", "limit": 1}

    for attempt in range(3):
        response = requests.get(search_url,headers=headers,params=params,timeout=30,)

        if response.status_code == 429:
            wait_seconds = int(response.headers.get("Retry-After", "1"))
            time.sleep(wait_seconds + 0.5)
            continue

        if 200 <= response.status_code < 300:
            data = response.json()
            items = data.get("tracks", {}).get("items", [])
            if items:
                return items[0]
            else:
                return None

        time.sleep(0.6 * (attempt + 1))

    response.raise_for_status()


def get_artist(artist_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{artists_url}/{artist_id}"

    for attempt in range(3):
        response = requests.get(url,headers=headers,timeout=30,)

        if response.status_code == 429:
            wait_seconds = int(response.headers.get("Retry-After", "1"))
            time.sleep(wait_seconds + 0.5)
            continue

        if 200 <= response.status_code < 300:
            return response.json()

        time.sleep(0.6 * (attempt + 1))

    response.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="Pull Spotify metadata for Kworb songs")
    parser.add_argument("--kworb",type=str,default=str(default_kworb_file),help="Path to input Kworb CSV (default: data/kworb_top_400.csv)",)
    parser.add_argument("--out",type=str,default=str(default_out_file),help="Output CSV path (default: data/spotify_from_kworb_400.csv)",)
    parser.add_argument("--limit",type=int,default=1000,help="Number of rows to process (default: 1000)",)
    args = parser.parse_args()
    kworb_path = Path(args.kworb)
    out_path = Path(args.out)
    row_limit = args.limit

    if not kworb_path.exists():
        print("ERROR:", kworb_path, "not found")
        return

    kworb_df = pd.read_csv(kworb_path)

    for column_name in ["Artist", "Title"]:
        if column_name not in kworb_df.columns:
            print("ERROR: Missing column",repr(column_name),"in",kworb_path.name,)
            return

    kworb_df["__order"] = range(len(kworb_df))

    kworb_df = (
        kworb_df.dropna(subset=["Artist", "Title"])
        .drop_duplicates(subset=["Artist", "Title"], keep="first")
        .sort_values("__order")
        .head(row_limit))

    print("Loaded", len(kworb_df), "Kworb rows to process")
    access_token = get_access_token()
    print("Token acquired")

    all_rows = []
    done_keys = set()

    if out_path.exists():
        existing_df = pd.read_csv(out_path)
        all_rows = existing_df.to_dict("records")
        for existing_row in all_rows:
            key = (
                normalize_text(existing_row.get("kworb_title")),
                normalize_text(existing_row.get("kworb_artist")))
            done_keys.add(key)
        print("Resuming from", len(all_rows), "already saved rows...")

    for i, kworb_row in kworb_df.iterrows():
        kworb_title = str(kworb_row["Title"])
        kworb_artist = str(kworb_row["Artist"])

        key = (normalize_text(kworb_title), normalize_text(kworb_artist))
        if key in done_keys:
            continue

        search_query = f"{kworb_title} {kworb_artist}"
        track_data = search_track_first(search_query, access_token)

        if not track_data:
            time.sleep(sleep_between_calls)
            continue

        primary_artist = track_data["artists"][0]
        primary_artist_id = primary_artist.get("id")

        record = {
            "_jn_name": normalize_text(track_data.get("name")),
            "_jn_artist": normalize_text(primary_artist.get("name")),
            "sp_track_id": track_data.get("id"),
            "name": track_data.get("name"),
            "artist_names": ", ".join(a.get("name", "") for a in track_data.get("artists", [])),
            "album_name": track_data.get("album", {}).get("name"),
            "release_date": track_data.get("album", {}).get("release_date"),
            "explicit": track_data.get("explicit"),
            "duration_ms": track_data.get("duration_ms"),
            "popularity": track_data.get("popularity"),
            "kworb_title": kworb_title,
            "kworb_artist": kworb_artist,
            "kworb_streams": kworb_row.get("Streams"),
            "kworb_daily_streams": kworb_row.get("Daily [streams]"),}

        if get_artist_stats and primary_artist_id:
            artist_data = get_artist(primary_artist_id, access_token) or {}
            record["primary_artist_id"] = primary_artist_id
            followers_info = artist_data.get("followers") or {}
            record["artist_followers"] = followers_info.get("total")
            record["artist_popularity"] = artist_data.get("popularity")
            genres = artist_data.get("genres", []) or []
            record["artist_genres"] = ", ".join(genres)

        all_rows.append(record)

        if len(all_rows) % checkpoint_every == 0:
            pd.DataFrame(all_rows).to_csv(out_path, index=False)
            print("Checkpoint: saved", len(all_rows), "rows →", out_path)

        time.sleep(sleep_between_calls)

    pd.DataFrame(all_rows).to_csv(out_path, index=False)
    print("Done. Saved", len(all_rows), "rows →", out_path)


if __name__ == "__main__":
    main()
