import os
from pathlib import Path
from dotenv import load_dotenv

from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

CLIENT_ID: str = os.getenv("CLIENT_ID", "")
CLIENT_SECRET: str = os.getenv("CLIENT_SECRET", "")
GENIUS_TOKEN: str = os.getenv("GENIUS_TOKEN", "")

PLAYLIST_NAME: str = "Clean Song Playlist"
OUTPUT_FILE: Path = Path("track_info.csv")
CLEAN_FILE: Path = Path("clean_tracks.csv")
EXPLICIT_FILE: Path = Path("explicit_tracks.csv")

SWEAR_WORDS: list = ['CUNT', 'SHIT', 'FUCK', 'BASTARD', 'TWAT', 'DICK', 'BITCH', 'PRICK', 'PISS', 'WANK']

def newSession():
    # authenticate
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )

    # create spotify session object
    session = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    return session

