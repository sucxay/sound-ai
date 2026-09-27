from typing import Optional
import subprocess 
import urllib.parse
from langchain.tools import tool 



def run_applescript(command: str):
    script = f'tell application "Music" to {command}'
    subprocess.run(['osascript', '-e', script], check=True)


@tool 
def play_music() -> str:
    """Play current song or resume playback in Apple Music."""
    try:
        run_applescript('play')
        return "Playing music in Apple Music."
    except subprocess.CalledProcessError:
        return "Failed to play music in Apple Music."


@tool 
def pause_music() -> str:
    """Pause the currently playing song in Apple Music."""
    try:
        run_applescript('pause')
        return "Music paused in Apple Music."
    except subprocess.CalledProcessError:
        return "Failed to pause music in Apple Music."


@tool
def next_track() -> str:
    """Play the next track in Apple Music."""
    try:
        run_applescript('next track')
        return "Skipped to next track."
    except subprocess.CalledProcessError:
        return "Failed to skip track."


@tool 
def previous_track() -> str:
    """Go back to the previous track in Apple Music."""
    try:
        run_applescript('previous track')
        return "Went back to previous track."
    except subprocess.CalledProcessError:
        return "Failed to go to previous track."


@tool 
def play_album(album: str, artist: Optional[str] = None) -> str:
    """Play an album by name in Apple Music, with optional artist filter.
    Args:
        album: the name of the album to play
        artist: optional artist name to narrow down results
    """
    clean_album = album.replace('"', '\\"')
    clean_artist = artist.replace('"', '\\"') if artist else ""

    script = f'''
    tell application "Music"
        activate
        set matchingTracks to (search playlist 1 for "{clean_album}")
        repeat with t in matchingTracks
            if "{clean_artist}" is "" or (artist of t contains "{clean_artist}") then
                play t
                return "OK"
            end if
        end repeat
        return "NOT_FOUND"
    end tell
    '''

    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True,
    )

    output = result.stdout.strip()

    if output == "OK":
        artist_suffix = f" by {artist}" if artist else ""
        return f"Playing album {album}{artist_suffix} from your Apple Music library."

    # Fallback: open Apple Music search URL
    search_query = f"{album} {artist}" if artist else album
    encoded_query = urllib.parse.quote(search_query)
    search_url = f"https://music.apple.com/us/search?term={encoded_query}"
    subprocess.run(['open', '-a', 'Music', search_url], capture_output=True, text=True)

    artist_suffix = f" by {artist}" if artist else ""
    return f"Album '{album}{artist_suffix}' was not found in your library. Opened Apple Music search for you."


@tool
def play_song(song: str, artist: Optional[str] = None) -> str:
    """Find and play a specific song from Apple Music.
    Args:
        song: the name of the song to play
        artist: optional artist name to narrow down results
    """
    clean_song = song.replace('"', '\\"')
    clean_artist = artist.replace('"', '\\"') if artist else ""

    script = f'''
    tell application "Music"
        activate
        set matchingTracks to (search playlist 1 for "{clean_song}")
        repeat with t in matchingTracks
            if "{clean_artist}" is "" or (artist of t contains "{clean_artist}") then
                play t
                return "OK"
            end if
        end repeat
        return "NOT_FOUND"
    end tell
    '''

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )

    output = result.stdout.strip()

    if output == "OK":
        artist_suffix = f" by {artist}" if artist else ""
        return f"Playing {song}{artist_suffix} from your Apple Music library."

    # Fallback: open Apple Music search URL
    search_query = f"{song} {artist}" if artist else song
    encoded_query = urllib.parse.quote(search_query)
    search_url = f"https://music.apple.com/us/search?term={encoded_query}"
    subprocess.run(['open', '-a', 'Music', search_url], capture_output=True, text=True)

    artist_suffix = f" by {artist}" if artist else ""
    return f"Song '{song}{artist_suffix}' was not found in your library. Opened Apple Music search for you."

