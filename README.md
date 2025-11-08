# What Makes a Song Popular?
Analyzing audio features and music video performance across platforms (Spotify + YouTube).

# Data sources

(STRUCTURE)
Data source
Name / short description
Source URL
Type
List of fields
Have you tried to access/collect data with python? yes/no
Estimated data size, number of data points you plan to use
	
Data1	Spotify
	Spotify Web API
	https://developer.spotify.com/ 
	API
	Popularity, track name, artist, album, release date, explicitly flag, duration
	Yes
	390
	
Data2	Kaggle
	Audio features and lyrics of spotify songs
	https://www.kaggle.com/datasets/imuhammad/audio-features-and-lyrics-of-spotify-songs 
	CSV
	Danceability, energy, tempo, valence, loudness, lyrics, genre
	no
	180000

Data3	Kworb
	Spotify most streamed songs of all time
	https://kworb.net/spotify/songs.html 
	Web page
	Song, total streams, daily streams
	yes
	2500

Data4	Kaggle
	Most Viewed YouTube Music Videos
	https://www.kaggle.com/datasets/asmonline/most-viewed-youtube-music-videos 
	CSV
	Video, total views
	no
	2500

# Results 
No results yet - progress report - I am able to extract data from Kworb webpage and Spotify API

# Installation
You must have/create a Spotify developer account and register an app to obtain your client ID and client secret.
These keys need to be saved in a .env file in the root directory of the project. See .env.example

To run dependencies, run:
	pip install -r requirements.txt

# Running analysis 

Activate your virtual environment
Then run
	python -m src.main