# What Makes a Song Popular?
Analyzing audio features and music video performance.

# Data sources

Data source
Name / short description
Source URL
Type
List of fields
Have you tried to access/collect data with python? yes/no
Estimated data size, number of data points you plan to use
	

Dataset 1 - Kworb

Name: Spotify most streamed songs of all time
Source: https://kworb.net/spotify/songs.html 
Type: Web page
Fields: Song, total streams, daily streams
Collected: Yes
Size: 1000 out of 2500

Dataset 2 - Spotify

Name: Spotify Web API
Source: https://developer.spotify.com/ 
Type: API
Fields: Popularity, track name, artist, album, release date, explicitly flag, duration
Collected: Yes
Size: 1000 songs
	
Dataset 3 - Kaggle

Name: Audio features and lyrics of spotify songs
Source: https://www.kaggle.com/datasets/imuhammad/audio-features-and-lyrics-of-spotify-songs 
Type: CSV
Fields: Danceability, energy, tempo, valence, loudness, lyrics, genre
Collected: Yes
Size: ~180000


Dataset 4 - Kaggle
Name: Most Viewed YouTube Music Videos
Source: https://www.kaggle.com/datasets/asmonline/most-viewed-youtube-music-videos 
Type: CSV
Fields: Video, total views
Collected: Yes
Size: 2500

# Results 

Key findings include: 
- "Acousticness" (a Spotify audio metric) had the highest correlation with total streams
- Songs with 4-6 minute ranges had a higher amount of streams on average
- Non-Explicit songs make up the vast majority of the top 400 songs
- Out of the top 400 songs, songs released in October performed the worst and songs released in February performed the best
- Songs with a tempo of 120-125 bpm perform best, with a significant drop in performance for songs with tempo <90 bpm and > 130 bpm
- Most common word in top 400 songs is 'love'

# Installation

1. Create a Spotify developer account and register an app to obtain your client ID and client secret.
2. These keys need to be saved in a .env file in the root directory of the project. See .env.example. 
3. You will also need to place your Kaggle API credentials into your ~/.kaggle/ folder 

Install dependences: pip install -r requirements.txt

# Running analysis 

Activate your virtual environment then run: python -m src.main