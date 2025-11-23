# src/scrape_kworb_top400.py
# scrape Kworb table
# output: data/kworb_top_400.csv

import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
import argparse
from src.config import data_folder, kworb_url, kworb_user_agent, kworb_output_filename

def clean_number(value):
    if pd.isna(value):
        return pd.NA
    value_str = str(value).replace(",", "").replace("\xa0", "").strip()
    return pd.to_numeric(value_str, errors="coerce")


def main():

    parser = argparse.ArgumentParser(description="Scrape Kworb top songs")
    parser.add_argument("--out",type=str,default=str(data_folder / kworb_output_filename),help="Output CSV path (default: data/kworb_top_400.csv)")
    parser.add_argument("--limit",type=int,default=1000,help="Number of rows to scrape (default: 1000)",)
    args = parser.parse_args()
    out_path = Path(args.out)
    limit = args.limit

    headers = {"User-Agent": kworb_user_agent}
    response = requests.get(kworb_url, headers=headers, timeout=30)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.addpos.sortable")

    if table is None:
        print("Error: could not find the Kworb table (class='addpos sortable').")
        return

    df = pd.read_html(str(table))[0]

    df.columns = [str(c).strip() for c in df.columns]

    if "Daily" in df.columns:
        daily_col = "Daily"
    else:
        daily_col = None
        for col in df.columns:
            if "Daily" in str(col):
                daily_col = col
                break

    if daily_col is None:
        print("Error: could not find a 'Daily' column in the Kworb table.")
        print("Columns found:", list(df.columns))
        return

    needed_columns = ["Artist and Title", "Streams", daily_col]
    for col in needed_columns:
        if col not in df.columns:
            print("Error: missing expected column:", col)
            print("Columns found:", list(df.columns))
            return

    df = df[needed_columns].head(limit).copy()

    split = df["Artist and Title"].astype(str).str.split(" - ", n=1, expand=True)
    df["Artist"] = split[0].str.strip()
    df["Title"] = split[1].str.strip()

    df["Streams"] = df["Streams"].apply(clean_number)
    df["Daily [streams]"] = df[daily_col].apply(clean_number)

    out_df = df[["Artist", "Title", "Streams", "Daily [streams]"]]
    out_df.to_csv(out_path, index=False)
    print("Saved", len(out_df), "rows →", out_path)


if __name__ == "__main__":
    main()
