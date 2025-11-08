# src/pull_spotify_kworb400.py
#       reads data/kworb_top_400.csv (columns: Artist, Title)
#       gets a Spotify access token using client credentials from .env
#       searches each song on Spotify and saves basic track metadata
#       fetches artist followers/popularity/genres per song
#       saves to data/spotify_from_kworb_400.csv

import os
import time
import base64
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

KWORB_CSV = DATA_DIR / "kworb_top_400.csv"
OUT_CSV = DATA_DIR / "spotify_from_kworb_400.csv"

LIMIT = 400
SLEEP_BETWEEN_CALLS = 0.12
CHECKPOINT_EVERY = 50
GET_ARTIST_STATS = True

TOKEN_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"
ARTISTS_URL = "https://api.spotify.com/v1/artists"

load_dotenv(ROOT / ".env")
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_access_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env")
    auth = f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
    b64 = base64.b64encode(auth).decode("utf-8")
    r = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {b64}"},
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]

def normalize(s: str) -> str:
    return (s or "").strip().lower()

def search_track_first(query: str, token: str) -> dict | None:
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": 1}
    for attempt in range(3):
        resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", "1"))
            time.sleep(wait + 0.5)
            continue
        if 200 <= resp.status_code < 300:
            items = resp.json().get("tracks", {}).get("items", [])
            return items[0] if items else None
        time.sleep(0.6 * (attempt + 1))
    resp.raise_for_status()

def get_artist(artist_id: str, token: str) -> dict | None:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{ARTISTS_URL}/{artist_id}"
    for attempt in range(3):
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", "1"))
            time.sleep(wait + 0.5)
            continue
        if 200 <= resp.status_code < 300:
            return resp.json()
        time.sleep(0.6 * (attempt + 1))
    resp.raise_for_status()

def main():
    if not KWORB_CSV.exists():
        print(f"ERROR: {KWORB_CSV} not found")
        return

    df = pd.read_csv(KWORB_CSV)
    for col in ["Artist", "Title"]:
        if col not in df.columns:
            print(f"ERROR: Missing column '{col}' in {KWORB_CSV.name}")
            return

    df["__order"] = range(len(df))
    df = (
        df.dropna(subset=["Artist", "Title"])
          .drop_duplicates(subset=["Artist", "Title"], keep="first")
          .sort_values("__order")
          .head(LIMIT)
    )

    token = get_access_token()
    print(f"Token acquired. Processing {len(df)} rows…")

    rows = []
    done_keys = set()
    if OUT_CSV.exists():
        existing = pd.read_csv(OUT_CSV)
        rows = existing.to_dict("records")
        for r in rows:
            k = (normalize(r.get("kworb_title")), normalize(r.get("kworb_artist")))
            done_keys.add(k)
        print(f"Resuming from {len(rows)} already-saved rows…")

    for i, row in df.iterrows():
        title = str(row["Title"])
        artist = str(row["Artist"])
        key = (normalize(title), normalize(artist))
        if key in done_keys:
            continue

        item = search_track_first(f"{title} {artist}", token)
        if not item:
            print(f"Not found: {title} — {artist}")
            time.sleep(SLEEP_BETWEEN_CALLS)
            continue

        primary = item["artists"][0]
        primary_id = primary.get("id")

        rec = {
            "_jn_name":   normalize(item.get("name")),
            "_jn_artist": normalize(primary.get("name")),
            "sp_track_id": item.get("id"),
            "name": item.get("name"),
            "artist_names": ", ".join(a.get("name","") for a in item.get("artists", [])),
            "album_name": item.get("album", {}).get("name"),
            "release_date": item.get("album", {}).get("release_date"),
            "explicit": item.get("explicit"),
            "duration_ms": item.get("duration_ms"),
            "popularity": item.get("popularity"),
            "kworb_title": title,
            "kworb_artist": artist,
            "kworb_streams": row.get("Streams"),
            "kworb_daily_streams": row.get("Daily [streams]"),
        }

        if GET_ARTIST_STATS and primary_id:
            a = get_artist(primary_id, token) or {}
            rec["primary_artist_id"] = primary_id
            rec["artist_followers"]  = (a.get("followers") or {}).get("total")
            rec["artist_popularity"] = a.get("popularity")
            rec["artist_genres"]     = ", ".join(a.get("genres", []) or [])

        rows.append(rec)

        if len(rows) % CHECKPOINT_EVERY == 0:
            pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
            print(f"Checkpoint: saved {len(rows)} rows → {OUT_CSV}")

        time.sleep(SLEEP_BETWEEN_CALLS)

    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    print(f"Done. Saved {len(rows)} rows → {OUT_CSV}")

if __name__ == "__main__":
    main()
