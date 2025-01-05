import os
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import time

# Set up logging
logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Script name
script_name = 'make-playlist.py'

# Log the start of the script
logging.info(f'**** {script_name} started ****')

# Load environment variables from .env file
load_dotenv()
logging.info('Environment variables loaded')

# Spotify credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope='playlist-modify-public'
))
logging.info('Spotify credentials set up')

# Check if the playlist already exists
playlist_name = 'Open Broadcast Tracks'
user_id = sp.current_user()['id']
logging.info(f'User ID: {user_id}')
playlists = sp.user_playlists(user_id)
playlist_id = None

for playlist in playlists['items']:
    if playlist['name'] == playlist_name:
        playlist_id = playlist['id']
        logging.info(f'Found existing playlist: {playlist_name} (ID: {playlist_id})')
        break

# Create a new playlist if it doesn't exist
if not playlist_id:
    playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
    playlist_id = playlist['id']
    logging.info(f'Created new playlist: {playlist_name} (ID: {playlist_id})')
else:
    # Clear the existing playlist
    sp.user_playlist_replace_tracks(user_id, playlist_id, [])
    logging.info(f'Cleared existing playlist: {playlist_name} (ID: {playlist_id})')

# Read track queries from file
track_queries = []
with open('tracks.txt', 'r') as file:
    track_queries = file.readlines()
logging.info(f'Read {len(track_queries)} track queries from tracks.txt')

# Function to retry API requests
def retry_request(func, *args, retries=3, delay=5, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f'Error: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})')
            time.sleep(delay)
    raise Exception(f'Failed after {retries} retries')

# Search for tracks and add them to the playlist
track_ids = []
for query in track_queries:
    # logging.info(f'Searching for track: {query.strip()}')
    offset = 0
    while True:
        result = retry_request(sp.search, q=query.strip(), type='track', limit=50, offset=offset)
        if result['tracks']['items']:
            track_id = result['tracks']['items'][0]['id']
            track_ids.append(track_id)
            # logging.info(f'Found track ID: {track_id} for query: {query.strip()}')
            break  # Only add the first found track for each query
        else:
            logging.info(f'No tracks found for query: {query.strip()}')
            break
logging.info(f'Found {len(track_ids)} track IDs')

# Add tracks to the playlist in batches of 100
for i in range(0, len(track_ids), 100):
    batch = track_ids[i:i + 100]
    retry_request(sp.user_playlist_add_tracks, user_id, playlist_id, batch)
    logging.info(f"Added {len(batch)} tracks to the playlist.")

# Log the end of the script
logging.info(f'**** {script_name} ended ****')
