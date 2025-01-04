import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# Set up logging
logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# URL to scrape
url = 'https://openbroadcast.ch/discover/tracks/'

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
service = Service('/opt/homebrew/bin/chromedriver')  # Path to chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    logging.info('**** Script started ****')  # Log the start of the script

    # Load the page
    driver.get(url)
    logging.info('Page loaded successfully')
    time.sleep(5)  # Wait for the page to load completely

    # Scroll to load more tracks, limited to 10 iterations
    last_height = driver.execute_script("return document.body.scrollHeight")
    iterations = 0
    while iterations < 10:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for new tracks to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        iterations += 1
        logging.info(f'Iteration {iterations}: Scrolled to bottom of page')

    # Get the page source and parse it with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    logging.info('Page source parsed with BeautifulSoup')

    # Write the complete response to a file for debugging
    with open('response.html', 'w', encoding='utf-8') as file:
        file.write(page_source)
    logging.info('Response written to response.html')

    # Find all track elements (adjust the selector based on the actual HTML structure)
    tracks = soup.find_all('div', class_='media-row')  # Replace 'div' and 'track' with actual tags/classes
    logging.info(f"Found {len(tracks)} tracks")

    # Write the tracks object to a file for debugging
    with open('tracks_debug.txt', 'w', encoding='utf-8') as file:
        for track in tracks:
            file.write(str(track))
            file.write('\n\n')
    logging.info("Tracks written to tracks_debug.txt")

    # Extract and write track information to file
    track_queries = []
    with open('tracks.txt', 'w') as file:
        for track in tracks:
            if len(track_queries) >= 200:
                break
            title_tag = track.find('div', class_='name').find('a')
            artist_tag = track.find('a', class_='artist__name')
            if title_tag and artist_tag:
                title = title_tag.text.strip()
                artist = artist_tag.text.strip()
                search_query = f"track:{title} artist:{artist}"
                file.write(search_query + '\n')
                track_queries.append(search_query)
            else:
                file.write("Title or artist not found for a track\n")
    logging.info("Track information extracted and written to tracks.txt")

except Exception as e:
    logging.error(f'Failed to retrieve content. Error: {e}')
finally:
    driver.quit()
    logging.info('Driver quit')
    logging.info('**** Script ended ****')  # Log the end of the script

"""
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

# Search for tracks and add them to the playlist
track_ids = []
for query in track_queries:
    offset = 0
    while True:
        result = sp.search(q=query, type='track', limit=50, offset=offset)
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
"""
