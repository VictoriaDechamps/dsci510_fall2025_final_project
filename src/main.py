# src/main.py

# scrape Kworb Top 1000 (originally 400 songs (hence filename), but wanted more data to analyse) 
# pull Spotify metadata for those 1000
# download kaggle audio+lyrics & merge

from pathlib import Path
from src.config import data_folder

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

def run_merge():
    from src.merge_spotify_kaggle1 import main as merge_main
    print("Step 3: downloading Kaggle data and merging with Spotify/Kworb")
    merge_main()
    print("Merged CSV created (spotify_kworb_kaggle1.csv).\n")

def run_merge_youtube():
    from src.merge_spotify_youtube import main as yt_main
    print("Step 4: Downloing youtube Kaggle data and merging with spotify_kworb_kaggle1")
    yt_main()
    print("Final merged CSV created: spotify_kworb_kaggle1_kaggle2.csv\n")

def run_analysis():
    from src.analysis_spotify import main as analysis_main
    print("Step 5: Running analysis on final merged dataset")
    analysis_main()
    print("Analysis complete\n")

def main():
    data_folder.mkdir(parents=True, exist_ok=True)
    run_scraper()
    run_spotify_pull()
    run_merge()
    run_merge_youtube()
    run_analysis()
    print("Finished.")
    print("Data folder:", data_folder)

if __name__ == "__main__":
    main()
