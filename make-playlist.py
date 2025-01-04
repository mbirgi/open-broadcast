import os
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(filename='app.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Script name
script_name = 'make-playlist.py'

# Log the start of the script
logging.info(f'**** {script_name} started ****')

# Load environment variables from .env file
load_dotenv()

# Spotify credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope='playlist-modify-public'
))

# Check if the playlist already exists
playlist_name = 'Open Broadcast Tracks'
user_id = sp.current_user()['id']
playlists = sp.user_playlists(user_id)
playlist_id = None

for playlist in playlists['items']:
    if playlist['name'] == playlist_name:
        playlist_id = playlist['id']
        break

# Create a new playlist if it doesn't exist
if not playlist_id:
    playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
    playlist_id = playlist['id']

# Read track queries from file
track_queries = []
with open('tracks.txt', 'r') as file:
    track_queries = file.readlines()

# Search for tracks and add them to the playlist
track_ids = []
for query in track_queries:
    offset = 0
    while True:
        result = sp.search(q=query.strip(), type='track', limit=50, offset=offset)
        if result['tracks']['items']:
            for item in result['tracks']['items']:
                track_id = item['id']
                track_ids.append(track_id)
            offset += 50
        else:
            break

if track_ids:
    sp.user_playlist_add_tracks(user_id, playlist_id, track_ids)
    logging.info(f"Added {len(track_ids)} tracks to the playlist.")
else:
    logging.info("No tracks found to add to the playlist.")

# Log the end of the script
logging.info(f'**** {script_name} ended ****')
