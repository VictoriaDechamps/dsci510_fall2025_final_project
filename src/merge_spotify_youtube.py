# src/merge_spotify_youtube.py
# combines spotify_kworb_kaggle1.csv with Kaggle "Most Viewed YouTube Music Videos"

import os
from pathlib import Path
import argparse
import kaggle
import pandas as pd
from src.config import (data_folder,kaggle_youtube_dataset,kaggle_youtube_subfolder,spotify_kworb_kaggle1_filename,spotify_kworb_kaggle1_kaggle2_filename)

def get_kaggle_youtube_data(dataset_name, extract_folder):
    try:
        kaggle.api.dataset_download_files(dataset_name,path=extract_folder,unzip=True,)

        csv_files = []
        for file_name in os.listdir(extract_folder):
            if file_name.lower().endswith(".csv"):
                csv_files.append(file_name)

        if not csv_files:
            print("Error: No CSV files found in Kaggle folder.")
            return None

        csv_path = os.path.join(extract_folder, csv_files[0])
        youtube_data = pd.read_csv(csv_path)
        return youtube_data

    except Exception as error:
        print("Error while loading Kaggle data:", error)
        return None

def normalize_text(value):
    if pd.notna(value):
        return str(value).strip().lower()
    else:
        return ""


def merge_spotify_youtube(spotify_csv_path, youtube_data, output_csv_path):
    spotify_path = Path(spotify_csv_path)
    if not spotify_path.exists():
        print("Error:", spotify_path, "does not exist")
        return

    spotify_data = pd.read_csv(spotify_path)

    if "name" not in spotify_data.columns:
        print("Error: Spotify dataset missing 'name' column")
        return
    if "Video" not in youtube_data.columns:
        print("Error: YouTube dataset missing 'Video' column")
        return

    spotify_data["name_norm"] = spotify_data["name"].apply(normalize_text)
    youtube_data["video_norm"] = youtube_data["Video"].apply(normalize_text)

    merged_rows = []
    for index, spotify_row in spotify_data.iterrows():
        track_name = spotify_row["name_norm"]

        youtube_matches = youtube_data[youtube_data["video_norm"].str.contains(track_name, na=False)]

        if not youtube_matches.empty:
            for index, youtube_row in youtube_matches.iterrows():
                combined_row = {}
                combined_row.update(spotify_row.to_dict())
                combined_row.update(youtube_row.to_dict())
                merged_rows.append(combined_row)

    merged_data = pd.DataFrame(merged_rows)
    merged_data.drop_duplicates(inplace=True)

    if "name" in merged_data.columns:
        merged_data.drop_duplicates(subset=["name"], keep="first", inplace=True)

    output_path = Path(output_csv_path)
    merged_data.to_csv(output_path, index=False)
    print("Saved merged dataset as:", output_path)

def main():
    parser = argparse.ArgumentParser(description="Merge Spotify+Kworb+Kaggle1 with YouTube Most Viewed Music Videos")
    parser.add_argument("--dataset",type=str,default=kaggle_youtube_dataset,help="Kaggle dataset slug for YouTube dataset",)
    parser.add_argument("--extract-dir",type=str,default=str(data_folder / kaggle_youtube_subfolder),help="Directory where Kaggle files are downloaded",)
    parser.add_argument("--spotify",type=str,default=str(data_folder / spotify_kworb_kaggle1_filename),help="Merged spotify+kworb+kaggle1 file",)
    parser.add_argument("--out",type=str,default=str(data_folder / spotify_kworb_kaggle1_kaggle2_filename),help="Final merged output file",)
    args = parser.parse_args()
    youtube_data = get_kaggle_youtube_data(args.dataset, args.extract_dir)
    if youtube_data is None:
        print("Could not load YouTube data")
        return

    merge_spotify_youtube(args.spotify, youtube_data, args.out)


if __name__ == "__main__":
    main()
