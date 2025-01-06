"""
This script scrapes track information from the Open Broadcast website and
writes the retrieved tracks to a file. It uses Playwright to load and parse
the webpage, BeautifulSoup to extract track details, and logs its progress
and any errors encountered during execution.
"""

import logging
from logging import FileHandler
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

# Set up logging
log_handler = FileHandler("app.log")
logging.basicConfig(
    handlers=[log_handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Script name
script_name = "main.py"

# Log the start of the script
logging.info(f"**** {script_name} started ****")

# Record the start time
start_time = datetime.now()

# Load environment variables from .env file
load_dotenv()

# URL to scrape
url = "https://openbroadcast.ch/discover/tracks/"

def scrape_tracks():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        logging.info("Page loaded successfully")

        # Scroll to load more tracks until the end of the page
        last_height = page.evaluate("document.body.scrollHeight")
        iterations = 0
        max_attempts = 5
        attempts = 0
        while attempts < max_attempts:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            # page.evaluate("window.scrollBy(0, 500)")  # Scroll down by 500px
            page.wait_for_timeout(10000)  # Wait for new tracks to load
            page.wait_for_load_state('networkidle') # Wait for network to be idle
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                attempts += 1
                logging.info(f"No new content loaded. Attempt {attempts}/{max_attempts}")
                # wait for 10 seconds before trying again
                page.wait_for_timeout(10000)
            else:
                attempts = 0
            last_height = new_height
            iterations += 1
            logging.info(
                f"Iteration {iterations}: Scrolled to bottom of page, "
                f"current height: {new_height}"
            )

        # Get the page source and parse it with BeautifulSoup
        page_source = page.content()
        soup = BeautifulSoup(page_source, "html.parser")
        logging.info("Page source parsed with BeautifulSoup")

        # Find all track elements (adjust the selector based on the actual HTML structure)
        tracks = soup.find_all(
            "div", class_="media-row"
        )  # Replace 'div' and 'track' with actual tags/classes
        logging.info(f"Found {len(tracks)} tracks")

        # Extract and write track information to file
        track_queries = []
        with open("tracks.txt", "w") as file:
            for track in tracks:
                title_tag = track.find("div", class_="name").find("a")
                artist_tag = track.find("a", class_="artist__name")
                if title_tag and artist_tag:
                    title = title_tag.text.strip()
                    artist = artist_tag.text.strip()
                    search_query = f"track:{title} artist:{artist}"
                    file.write(search_query + "\n")
                    track_queries.append(search_query)
                else:
                    file.write("Title or artist not found for a track\n")
        logging.info("Track information extracted and written to tracks.txt")

        browser.close()

try:
    scrape_tracks()
except Exception as e:
    logging.error(f"Failed to retrieve content. Error: {e}")

# Calculate and log the total run time
end_time = datetime.now()
total_run_time = end_time - start_time
logging.info(f"Total run time: {total_run_time}")

logging.info(f"**** {script_name} ended ****")
