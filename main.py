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
logging.basicConfig(filename='app.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Script name
script_name = 'main.py'

# Log the start of the script
logging.info(f'**** {script_name} started ****')

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

    # Find all track elements (adjust the selector based on the actual HTML structure)
    tracks = soup.find_all('div', class_='media-row')  # Replace 'div' and 'track' with actual tags/classes
    logging.info(f"Found {len(tracks)} tracks")

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
    logging.info(f'**** {script_name} ended ****')  # Log the end of the script
