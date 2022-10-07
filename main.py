import os
import csv
import re

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
GENIUS_TOKEN = os.getenv("GENIUS_TOKEN", "")

OUTPUT_FILE_NAME = "track_info.csv"

CLEAN_FILE = "clean_tracks.csv"

genius = lyricsgenius.Genius(GENIUS_TOKEN)

SWEAR_WORDS = ['CUNT', 'SHIT', 'FUCK', 'BASTARD', 'TWAT', 'DICK', 'BITCH', 'DICKHEAD']


def getPlaylist():
    playlistLink = input("Enter playlist link")
    return playlistLink


def getTracks():
    PLAYLIST_LINK = getPlaylist()

    # authenticate
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )

    # create spotify session object
    session = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # get uri from https link
    if match := re.match(r"https://open.spotify.com/playlist/(.*)\?", PLAYLIST_LINK):
        playlist_uri = match.groups()[0]
    else:
        raise ValueError("Expected format: https://open.spotify.com/playlist/...")

    # get list of tracks in a given playlist (note: max playlist length 100)
    offset = 0
    tracks = []

    for i in range(0, 500, 100):
        tracks += session.playlist_tracks(playlist_uri, offset=offset)["items"]
        offset += 100

    return tracks


def generateCSV(tracks):
    # create csv file
    with open(OUTPUT_FILE_NAME, "a", encoding="utf-8") as file:
        writer = csv.writer(file)

        # write header column names
        writer.writerow(["track", "artist"])

        # extract name and artist
        for track in tracks:
            name = track["track"]["name"]
            artists = ", ".join(
                [artist["name"] for artist in track["track"]["artists"]]
            )

            # write to csv
            writer.writerow([name, artists])


def getLyrics() -> None:
    with open(OUTPUT_FILE_NAME, newline='') as file:
        reader = csv.DictReader(file)
        writer = csv.writer(file)

        for row in reader:
            artist, track = row['artist'], row['track']

            song = genius.search_song(title=track, artist=artist)

            explicit = checkExplicit(song)
            print(explicit)

            if not explicit:
                cleanSongs(artist, track)


def cleanSongs(artist, track) -> None:
    with open(CLEAN_FILE, "a", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([artist, track])


def checkExplicit(song) -> bool:
    lyrics = song.lyrics.upper().split()

    print(lyrics)

    if any(word in lyrics for word in SWEAR_WORDS):
        return True


def main() -> None:
    initialise()

    # gets the tracks to a playlist, and saves them to a csv file
    tracks = getTracks()
    generateCSV(tracks)

    getLyrics()


def initialise() -> None:
    if os.path.exists(CLEAN_FILE):
        os.remove(CLEAN_FILE)

    if os.path.exists(OUTPUT_FILE_NAME):
        os.remove(OUTPUT_FILE_NAME)


if __name__ == '__main__':
    main()
