import os
from pathlib import Path
import csv
import re

from config import *

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius


genius = lyricsgenius.Genius(GENIUS_TOKEN)



def getPlaylist() -> str:
    playlistLink = input("Enter playlist link: ")
    return playlistLink


def newSession():
    # authenticate
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )

    # create spotify session object
    session = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    return session


def getTracks() -> list:
    PLAYLIST_LINK = getPlaylist()

    session = newSession()

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

    print('complete')
    return tracks


def generateCSV(tracks) -> None:
    # create csv file
    with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
        writer = csv.writer(file)

        # write header column names
        writer.writerow(["track", "artist", "id", "url"])

        # extract name and artist
        for track in tracks:
            name = track["track"]["name"]
            artists = ", ".join(
                [artist["name"] for artist in track["track"]["artists"]]
            )

            url = track['track']['external_urls']['spotify']
            ID = track["track"]["id"]

            # write to csv
            writer.writerow([name, artists, ID, url])


def getLyrics() -> None:
    with open(OUTPUT_FILE, newline='') as file:
        reader = csv.DictReader(file)

        for row in reader:
            artist, track, ID, url = row['artist'], row['track'], row['id'], row['url']

            song = genius.search_song(title=track, artist=artist)

            explicit = checkExplicit(song)
            print(explicit)

            if not explicit:
                cleanSongs(artist, track, ID, url)

            else:
                explicitSongs(artist, track, ID, url)


def explicitSongs(artist, track, ID, url) -> None:
    with open(EXPLICIT_FILE, "a", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([artist, track, ID, url])


def cleanSongs(artist, track, ID, url) -> None:
    with open(CLEAN_FILE, "a", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([artist, track, ID, url])


def checkExplicit(song) -> bool:
    if song is None:
        return True

    lyrics = song.lyrics.upper().replace('[', '').replace(']', '').split()

    print(lyrics)

    for word in lyrics:
        if any(swear in word for swear in SWEAR_WORDS):
            return True


def main() -> None:
    initialise()

    # gets the tracks to a playlist, and saves them to a csv file
    tracks = getTracks()
    generateCSV(tracks)

    getLyrics()


def initialise() -> None:
    CLEAN_FILE.unlink(missing_ok=True)
    OUTPUT_FILE.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
