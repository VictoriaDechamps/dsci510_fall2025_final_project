# src/config.py

from pathlib import Path
from dotenv import load_dotenv
import os

root_folder = Path(__file__).resolve().parents[1]
data_folder = root_folder / "data"
results_folder = root_folder / "results"

env_path = root_folder / ".env"
load_dotenv(dotenv_path=env_path)

kworb_url = "https://kworb.net/spotify/songs.html"
kworb_user_agent = "Mozilla/5.0 (educational project script)"
kworb_output_filename = "kworb_top_400.csv"

spotify_token_url = "https://accounts.spotify.com/api/token"
spotify_search_url = "https://api.spotify.com/v1/search"
spotify_artists_url = "https://api.spotify.com/v1/artists"

spotify_from_kworb_filename = "spotify_from_kworb_400.csv"

sleep_between_calls = 0.12
checkpoint_every = 50
get_artist_stats = True

spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

kaggle_audio_dataset = "imuhammad/audio-features-and-lyrics-of-spotify-songs"
kaggle_audio_subfolder = "kaggle_audio_lyrics"

spotify_kworb_kaggle1_filename = "spotify_kworb_kaggle1.csv"

kaggle_youtube_dataset = "asmonline/most-viewed-youtube-music-videos"
kaggle_youtube_subfolder = "kaggle_youtube"

spotify_kworb_kaggle1_kaggle2_filename = "spotify_kworb_kaggle1_kaggle2.csv"

spotify_green = "#1DB954"
text_color = "black"
bg_color = "white"

audio_feature_columns = ["danceability","energy","loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo"]


