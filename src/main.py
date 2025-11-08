# src/main.py
# so far: 
# 1) scrape Kworb Top 400 → data/kworb_top_400.csv
# 2) pull Spotify metadata for those 400 → data/spotify_from_kworb_400.csv

from pathlib import Path

def run_scraper():
    from src.scrape_kworb_top400 import main as scrape_main
    print("Step 1: Scraping Kworb Top 400")
    scrape_main()
    print("Kworb CSV created.\n")

def run_spotify_pull():
    try:
        from src.pull_spotify_kworb400 import main as pull_main
    except ModuleNotFoundError:
        from src.pull_spotify_kworb400_simple import main as pull_main

    print("Step 2: Pulling Spotify data for 400 songs")
    pull_main()
    print("Spotify CSV created.\n")

def main():
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    run_scraper()
    run_spotify_pull()

    print("Finished.")
    print(f"Data folder: {data_dir}")

if __name__ == "__main__":
    main()
