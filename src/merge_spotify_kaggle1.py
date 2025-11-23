# src/merge_spotify_kaggle.py

# download Kaggle dataset: "Audio features and lyrics of Spotify songs"
# merge with spotify_from_kworb_400.csv
# save merged as spotify_kworb_kaggle1.csv

import os
from pathlib import Path
import argparse
import kaggle
import pandas as pd
from src.config import (data_folder,kaggle_audio_dataset,kaggle_audio_subfolder,spotify_from_kworb_filename,spotify_kworb_kaggle1_filename)



def get_kaggle_data(dataset_name, extract_folder):
    print("Loading data from Kaggle:", dataset_name)

    try:
        kaggle.api.dataset_download_files(dataset_name, path=extract_folder, unzip=True)

        csv_files = []
        for file_name in os.listdir(extract_folder):
            full_path = os.path.join(extract_folder, file_name)
            if os.path.isfile(full_path) and file_name.lower().endswith(".csv"):
                csv_files.append(file_name)

        if not csv_files:
            print("Error: no CSV files found in folder:", extract_folder)
            return None

        csv_file = os.path.join(extract_folder, csv_files[0])
        kaggle_data = pd.read_csv(csv_file)
        return kaggle_data

    except Exception as error:
        print("Error loading data from Kaggle:", error)
        return None


def normalize_text(value):
    if pd.notna(value):
        return str(value).strip().lower()
    else:
        return ""


def merge_spotify_and_kaggle(spotify_file, kaggle_data, output_file):
    spotify_path = Path(spotify_file)
    if not spotify_path.exists():
        print("Error: Spotify file not found:", spotify_path)
        return

    spotify_data = pd.read_csv(spotify_path)

    for column_name in ["name", "artist_names"]:
        if column_name not in spotify_data.columns:
            print("Error: Spotify file is missing column:", column_name)
            return

    for column_name in ["track_name", "track_artist"]:
        if column_name not in kaggle_data.columns:
            print("Error: Kaggle data is missing column:", column_name)
            return

    spotify_data["primary_artist"] = (spotify_data["artist_names"].astype(str).str.split(",", n=1).str[0])

    spotify_data["merge_key"] = (spotify_data["name"].apply(normalize_text)+ " - "+ spotify_data["primary_artist"].apply(normalize_text))
    kaggle_data["merge_key"] = (kaggle_data["track_name"].apply(normalize_text)+ " - "+ kaggle_data["track_artist"].apply(normalize_text))

    merged_data = pd.merge(spotify_data,kaggle_data,on="merge_key",how="inner",suffixes=("_spotify", "_kaggle"),)

    rows_before = len(merged_data)
    merged_data = merged_data.drop_duplicates(subset=["merge_key"], keep="first")
    rows_after = len(merged_data)

    output_path = Path(output_file)

    merged_data.to_csv(output_path, index=False)

def main():
    parser = argparse.ArgumentParser(description="Download Kaggle audio+lyrics data and merge with Spotify Kworb data")
    parser.add_argument("--dataset",type=str,default=kaggle_audio_dataset,help="Kaggle dataset slug")
    parser.add_argument("--extract-dir",type=str,default=str(data_folder / kaggle_audio_subfolder),help="Folder to extract Kaggle files into")
    parser.add_argument("--spotify",type=str,default=str(data_folder / spotify_from_kworb_filename),help="Path to Spotify+Kworb CSV")
    parser.add_argument("--out",type=str,default=str(data_folder / spotify_kworb_kaggle1_filename),help="Output CSV path")
    args = parser.parse_args()
    kaggle_data = get_kaggle_data(args.dataset, args.extract_dir)
    if kaggle_data is None:
        print("Could not load Kaggle data")
        return

    merge_spotify_and_kaggle(args.spotify, kaggle_data, args.out)


if __name__ == "__main__":
    main()
