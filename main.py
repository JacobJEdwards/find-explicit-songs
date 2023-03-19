#!/usr/bin/env python3

from pathlib import Path
import csv
import re

from config import *

session = newSession()


# Returns the uri of the playlist is valid for use with the spotipy library
def getPlaylist() -> str:
    PLAYLIST_LINK: str = input("Enter playlist link: ")

    # get uri from https link and check if valid
    if match := re.match(r"https://open.spotify.com/playlist/(.*)\?", PLAYLIST_LINK):
        playlist_uri = match.groups()[0]
    else:
        raise ValueError("Expected format: https://open.spotify.com/playlist/...")

    return playlist_uri


# Get the list of tracks in the spotify playlist using the spotipy libray
def getTracks() -> list:
    playlist_uri = getPlaylist()

    # get list of tracks in a given playlist (note: max playlist length 100)
    offset = 0
    tracks = []

    for i in range(0, 500, 100):
        tracks += session.playlist_tracks(playlist_uri, offset=offset)["items"]
        offset += 100

    print("complete")
    return tracks


# Generates a CSV of all the tracks in the playlist
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

            url = track["track"]["external_urls"]["spotify"]
            ID = track["track"]["id"]

            # write to csv
            writer.writerow([name, artists, ID, url])


def getLyrics(file) -> None:
    # Reads the list of tracks in the playlist from the designated file
    with open(file, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            artist, track, ID, url = row["artist"], row["track"], row["id"], row["url"]

            # retrieves song information using the genius api
            song = genius.search_song(title=track, artist=artist)

            # chekcs if the song is explicit
            explicit = checkExplicit(song)
            print(explicit)

            # Adds the song to the correct file
            writeCSV(artist, track, ID, url, explicit)


# Function used to write the song information to the correct files
def writeCSV(artist: str, track: str, ID: str, url: str, explicit: bool) -> None:
    # writes to the correct file
    if explicit:
        file = EXPLICIT_FILE
    else:
        file = CLEAN_FILE

    with open(file, "a", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([artist, track, ID, url])


# Checks if the lyrics contain any banned words
def checkExplicit(song) -> bool:
    if song is None:
        return True

    lyrics = song.lyrics.upper().replace("[", "").replace("]", "").split()

    print(lyrics)

    for word in lyrics:
        if any(swear in word for swear in SWEAR_WORDS):
            return True

    return False


def main() -> None:
    initialise(remove_files=True)

    # gets the tracks to a playlist, and saves them to a csv file
    try:
        tracks = getTracks()
    except ValueError as e:
        print(e)
        print("Exiting...")
        return 

    generateCSV(tracks)

    getLyrics(OUTPUT_FILE)


def initialise(remove_files=True) -> None:
    if remove_files:
        CLEAN_FILE.unlink(missing_ok=True)
        OUTPUT_FILE.unlink(missing_ok=True)
        EXPLICIT_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
