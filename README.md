# Open Broadcast Tracks Scraper and Spotify Playlist Creator

This Python script scrapes track information from the Open Broadcast website and creates a Spotify playlist with the retrieved tracks. It uses Playwright to load and parse the webpage, BeautifulSoup to extract track details, and Spotipy to interact with the Spotify API.

**Currently not working properly, scrolling of the dynamically loaded page (with
javascript) does not work until the end, but stops randomly after a number of scrolls**

## Features
- Scrapes track titles and artist names from the Open Broadcast website.
- Checks if a Spotify playlist with the specified name already exists.
- Creates a new Spotify playlist if it doesn't exist.
- Clears the existing playlist before adding new tracks.
- Adds all found tracks to the Spotify playlist without a limit.

## Requirements
- Python 3.x
- Playwright
- BeautifulSoup4
- Spotipy
- python-dotenv
- ChromeDriver

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/mbirgi/open-broadcast.git
   cd open-broadcast
