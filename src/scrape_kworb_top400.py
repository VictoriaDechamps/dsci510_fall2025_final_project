# src/scrape_kworb_top400.py
# scrape Kworb table, only first 400 rows
# output: data/kworb_top_400.csv

import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

URL = "https://kworb.net/spotify/songs.html"

def clean_number(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).replace(",", "").replace("\xa0", "").strip()
    return pd.to_numeric(s, errors="coerce")

def main():
    ROOT = Path(__file__).resolve().parents[1]
    DATA_DIR = ROOT / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT = DATA_DIR / "kworb_top_400.csv"

    headers = {"User-Agent": "Mozilla/5.0 (educational project script)"}
    html = requests.get(URL, headers=headers, timeout=30).text

    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table.addpos.sortable")
    if table is None:
        raise RuntimeError("Could not find the Kworb table (class='addpos sortable').")

    df = pd.read_html(str(table))[0]

    df.columns = [str(c).strip() for c in df.columns]

    daily_col = "Daily" if "Daily" in df.columns else [c for c in df.columns if "Daily" in c][0]
    keep = ["Artist and Title", "Streams", daily_col]
    for c in keep:
        if c not in df.columns:
            raise RuntimeError(f"Missing expected column '{c}'. Got: {list(df.columns)}")
    df = df[keep].head(400).copy()

    split = df["Artist and Title"].astype(str).str.split(" - ", n=1, expand=True)
    df["Artist"] = split[0].str.strip()
    df["Title"] = split[1].str.strip()

    df["Streams"] = df["Streams"].apply(clean_number)
    df["Daily [streams]"] = df[daily_col].apply(clean_number)

    out = df[["Artist", "Title", "Streams", "Daily [streams]"]]
    out.to_csv(OUT, index=False)
    print(f"Saved {len(out)} rows → {OUT}")

if __name__ == "__main__":
    main()
