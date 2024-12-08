# lyrics_fetcher.py
import requests
from bs4 import BeautifulSoup

class LyricsFetcher:
    """Class responsible for fetching song lyrics from the web."""
    BASE_SEARCH_URL = "https://www.google.com/search?q={query}"

    @staticmethod
    def fetch_lyrics(song_name, artist_name=None):
        """Fetch lyrics for the given song."""
        try:
            query = f"{song_name} lyrics"
            if artist_name:
                query += f" {artist_name}"
            
            search_url = LyricsFetcher.BASE_SEARCH_URL.format(query=query.replace(" ", "+"))
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(search_url, headers=headers)

            if response.status_code != 200:
                return f"Failed to fetch lyrics: HTTP {response.status_code}"

            soup = BeautifulSoup(response.text, "html.parser")
            lyrics_div = soup.find("div", class_="BNeawe tAd8D AP7Wnd")  
            if lyrics_div:
                return lyrics_div.get_text()

            return "Lyrics not found."
        except requests.RequestException as e:
            return f"Network error: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
