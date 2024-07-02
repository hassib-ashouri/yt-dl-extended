import sys
import logging
from spotdl import Spotdl
from ytmusicapi import YTMusic
import yt_dlp
from unicodedata import normalize
import re

# use spotdl to get songs names from a spotify playlist
def get_songs_from_playlist(playlist_url):
    songs = []
    songs = spotdl.search([playlist_url])
    return songs

def is_left_contained_in_right(contained, container):
    algo = "NFC"
    container = normalize("NFKD", container.lower())
    container = re.sub(r"[\u0027\u02B9\u02BB\u02BC\u02BE\u02C8\u02EE\u0301\u0313\u0315\u055A\u05F3\u07F4\u07F5\u1FBF\u2018\u2019\u2032\uA78C\uFF07]", "'",container)
    contained = normalize("NFKD", contained.lower())
    contained = re.sub(r"[\u0027\u02B9\u02BB\u02BC\u02BE\u02C8\u02EE\u0301\u0313\u0315\u055A\u05F3\u07F4\u07F5\u1FBF\u2018\u2019\u2032\uA78C\uFF07]", "'",contained)
    isContained = contained in container
    return isContained

def get_valid_songs(search_results, artist, title):
    validSongs = []
    # normalize the strings using nfkd
    
    for i in range(len(search_results)):
        each_song = search_results[i]
        # normalize

        isValidArtist = False
        isValidTitle = False

        # assumed matched if no artist is provided
        if(len(each_song['artists']) == 0): 
            isValidArtist = True
        else:
            for each_artist in each_song['artists']:
                if(is_left_contained_in_right(artist, each_artist['name'])):
                    isValidArtist = True
                    break

        if(is_left_contained_in_right(title, each_song['title'])):
            isValidTitle = True

        logging.debug("isValidArtist:", isValidArtist, "isValiedTitle:", isValidTitle)
        if(isValidArtist and isValidTitle):
            validSongs.append(each_song)

    return validSongs

def get_extended_song(valid_songs):
    extended_song_i = -1

    for i in range(len(valid_songs)):
        each_song = valid_songs[i]
        each_song_title = each_song['title']

        if("Extended" in each_song_title):
            extended_song_i = i

    logging.debug("extended_song_i:", extended_song_i)
    return extended_song_i


def print_yt_songs_dic(search_results):
    i = 1
    for k,v in search_results.items():
        print(i, " - ",get_yt_song_preview(v))
        i += 1

def print_yt_songs(search_results):
    for i in range(len(search_results)):
        each_song = search_results[i]
        print(i, " - ",get_yt_song_preview(each_song))

def get_yt_song_preview(song):
    return f"{song['artists']} - {song['title']} - {song['duration']}"

def init_spotdl():
    # use the spotdl defaults for this
    spotdl = Spotdl(client_id ="5f573c9620494bae87890c0f08a60293", client_secret= "212476d9b0f3472eaa762d90b19b0ba8")
    return spotdl

def init_ytmusic():
    ytmusic = YTMusic()
    return ytmusic

if __name__ == '__main__':

    if(len(sys.argv) < 2):
        print("Usage: python3 main.py <spotify_playlist_url>")
        sys.exit(1)

    spotdl = init_spotdl()
    ytmusic = init_ytmusic()

    playtlist_songs = get_songs_from_playlist(sys.argv[1])
    print("songs in spotify playlist: ")
    for i in range(len(playtlist_songs)):
        print(i, " - ", playtlist_songs[i].artist, " - ", playtlist_songs[i].name, " - ", playtlist_songs[i].duration)
    # normalize spotify types to yt types
    songs_to_lookup = [f"{song.artist}-{song.name}-Extended" for song in playtlist_songs]
    print("songs to lookup: ", songs_to_lookup)
    songs_to_download = {}

    # Some key metrics to keep track
    extended_songs_found = 0

    for i in range(len(songs_to_lookup)):
        print("=====================================================================")
        artist, title = songs_to_lookup[i].split("-")[0:2]
        print("Searching yt for:", songs_to_lookup[i])
        print("artist:", artist, "title:", title)
        results = ytmusic.search(songs_to_lookup[i], filter='songs')
        print("Found: ", len(results), " songs")

        # filter valid songs that match the artist and title
        valid_songs = get_valid_songs(results, artist, title)

        #default to the first song of the search results
        song_to_download = results[0]

        # guard clause
        if(len(valid_songs) == 0):
            print(f"No valid songs found in the search for {songs_to_lookup[i]}. Printting search results")
            print_yt_songs(results)
            continue

        print("Valid songs:")
        print_yt_songs(valid_songs)

        # find the song to download
        # find extended version
        extended_song_i = get_extended_song(valid_songs)

        # if extended version not found, get the first song which probably is the original version
        if(extended_song_i > -1):
            song_to_download = valid_songs[extended_song_i]
            extended_songs_found += 1
            print("Found extended version")
        else:
            song_to_download = valid_songs[0]
            print("No extended version found. Downloading the first song")


        print("Adding song to download:")
        print(get_yt_song_preview(song_to_download))
        songs_to_download[f"{song_to_download['artists'][0]['name'] if len(song_to_download['artists']) > 0 else ""} - {song_to_download['title']}"] = song_to_download

    print("=====================================================================")
    print("Summary:")
    print("Songs in the original playlist:", len(playtlist_songs))
    print("Extended songs found:", extended_songs_found)
    print("Total songs to download:", len(songs_to_download))
    print("songs to download:")
    print_yt_songs_dic(songs_to_download)


    # use yt_dlp to download the songs
    with yt_dlp.YoutubeDL({
        'outtmpl': "%(title)s.%(ext)s",
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }, {
            'key': 'FFmpegMetadata',
        }],
        }) as ydl:
        # download the songs
        for each_song_string, each_song in songs_to_download.items():
            print("Downloading song: ", each_song_string)
            ydl.download(f"https://music.youtube.com/watch?v={each_song['videoId']}")


