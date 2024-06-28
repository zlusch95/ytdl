import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import re
import emoji
import mutagen
import os
import getpass
import subprocess


ydl_opts = {
    "paths": {},
    "download_archive": "",
    "extract_flat": True,
    "ignoreerrors": True,
    "outtmpl": {"default": "%(title)s.%(ext)s"},
    "format": "bestaudio/best",
    "noplaylist": True,
    "writethumbnail": True,  # save video image (thumbnail)
    "restrictfilenames": False,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "flac",  # change to flac if preferred (ffmpeg not configured for soundcloud yet)
            "preferredquality": "320",
        },
        {
            "key": "FFmpegMetadata",
            "add_metadata": True,
        },
        {"key": "EmbedThumbnail"},  # embed thumbnail
    ],
}

# set this user agent to enable metadata extraction
yt_dlp.utils.std_headers["User-Agent"] = (
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
)


def handleSong(url, path="/Users/tilschulz/Music/dj/techno6"):
    ydl_opts["paths"] = {"home": path}
    ydl_opts["download_archive"] = path + "/" + "history.txt"
    ydl_opts["extract_flat"] = False
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            url,
            download=False,
        )
        if info:  # if it was downloaded already, info object is None
            downloadSong(ydl, url, info, path, downloadAll=True)


def handlePlaylist(url, path="/Users/tilschulz/Music/dj/techno7"):
    ydl_opts["paths"] = {"home": path}
    ydl_opts["download_archive"] = path + "/" + "history.txt"
    ydl_opts["noplaylist"] = False
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        infoPlaylist = ydl.extract_info(
            url,
            download=False,
        )
        entries = infoPlaylist["entries"]
        leftovers = []
        newSongPaths = []
        print("Playlist ID:", infoPlaylist["id"])
        print(
            "Total playlist videos:", infoPlaylist["playlist_count"]
        )  # amount of all playlist videos
        print(
            "Videos to be downloaded:", len(entries)
        )  # amount of videos not downloaded yet
        vidCounter = 1
        for entry in entries:
            if not entry:
                print("ERROR: Unable to get info. Continuing...")
            else:
                # print(entry["webpage_url"])
                songURL = entry["url"]
                info = ydl.extract_info(songURL, download=False)
                print("Download Song {} of {} ...".format(vidCounter, len(entries)))
                postData = downloadSong(
                    ydl, songURL, info, path, downloadAll=True
                )  # Set downloadAll to True if you want to download every video in playlist
                # print(postData)
                if not postData[0]:
                    leftovers.append(postData[1])
                elif not postData[1]:
                    newSongPaths.append(postData[0])
            vidCounter += 1
        if leftovers != []:
            print(
                "Videos not downloaded because they didn't match song pattern: ",
                leftovers,
            )
        try:
            os.remove(path + "/" + infoPlaylist["title"] + ".jpg")
        except FileNotFoundError as e:
            print("Playlist picture was not founded", e)
        print("Successfully downloaded playlist!")

        return newSongPaths


def downloadSong(ydl, url, info, path, downloadAll=False):
    def rename():
        newFilePath = path + "/" + artistTrack[0] + " - " + artistTrack[1] + ".mp3"
        os.rename(mp3Path, newFilePath)
        return newFilePath

    def isSongPattern():
        if metaData and (
            duration <= 900
        ):  # Asumption: Track is not longer than 15 min = 900 sec
            return True
        elif not metaData and info.get(
            "track", False
        ):  # YT song pattern - just the song is the title, track is provided though
            return True
        return False

    title = info["title"]
    renameFile = False
    if (
        not "-" in title
    ):  # change filename later to be format 'artist - track' instead of just 'track'
        renameFile = True
    duration = info["duration"]
    metaData = extractSongMetaData(title)  # song pattern recognition
    mp3Path = path + "/" + title + ".mp3"
    if (
        isSongPattern()
    ):  # metadata was extracted and was not provided by url --> set metadata
        ydl.download([url])
        artistTrack = handleSongMetaData(metaData, info, mp3Path)
        if renameFile:
            mp3Path = rename()
    else:
        if not downloadAll:  # download only song pattern
            print(
                emoji.emojize(
                    ":cross_mark: Could not identify a song pattern for video '{}'"
                ).format(title)
            )
            print("Download just songs, skip video!")
            return (None, (url, title))
        else:
            print("Download audio of video '{}'".format(title))
            ydl.download([url])
            # yt_dlp sets title as track & uploader as artist per default
            # handleOtherMetaData(mp3Path)
    return (mp3Path, None)


def handleSongMetaData(metaData, info, mp3Path):
    def noMetaDataProvided():
        return not info.get("track", False) and metaData

    def metaDataProvidedButIncorrect():
        if info.get("track", False) and metaData:
            return metaData[0] != info["artist"] or metaData[1] != info["track"]

    def setSongMetaData():
        print("Artist:", metaData[0])
        print("Track:", metaData[1])
        try:
            audio = EasyID3(mp3Path)
            audio["artist"] = metaData[0]
            audio["title"] = metaData[1]
            audio.save()
        except (FileNotFoundError, mutagen.MutagenError) as e:
            print(
                "Error: yt_dlp extracted different filename. Keep default yt_dlp metadata instead"
            )

    def setAlbumAndGenre():
        try:
            audio = EasyID3(mp3Path)
            audio["album"] = "ytdl"
            audio["genre"] = "Techno"
            audio.save()
        except (FileNotFoundError, mutagen.MutagenError) as e:
            print(
                "Error: yt_dlp extracted different filename. Keep default yt_dlp metadata instead"
            )

    setAlbumAndGenre()
    if noMetaDataProvided():
        setSongMetaData()
        print(emoji.emojize(":test_tube: Extracted metadata from title"))
        return metaData
    elif metaDataProvidedButIncorrect():
        setSongMetaData()
        print(
            emoji.emojize(
                ":red_exclamation_mark: Url metadata does not match title information. Extracted from title instead!"
            )
        )
        return metaData
    else:
        print(emoji.emojize(":check_mark_button: Url provided correct metadata"))
        print(info["artist"], " - ", info["track"])
        return [info["artist"], info["track"]]


def handleOtherMetaData(mp3Path):
    def setOtherMetaData():
        audio = EasyID3(mp3Path)
        audio["artist"] = ""
        audio.save()

    setOtherMetaData()


def extractSongMetaData(title):
    if not "-" in title:
        return False
    brackets = r"\[.*?\]"
    parentheses = r"(\(.*?\)).(\(.*?\))"
    title = re.sub(brackets, "", title)
    if re.match(parentheses, title):
        secondParentheses = re.search(parentheses, title).group(2)
        title = title.replace(secondParentheses, "")
    meta = title.split("-", 1)  # meta[0] = artist, meta[1] = track
    metaData = []
    # delete whitespaces at beginning and end
    for tag in meta:
        if tag[-1] == " ":
            tag = tag[:-1]
        if tag[0] == " ":
            tag = tag[1:]
        metaData.append(tag)
    return metaData


def download(url):
    if "playlist" in url or "sets" in url:  # playlist (YouTube), sets (Soundcloud)
        return handlePlaylist(url)
    else:
        handleSong(url)


def addToAppleMusic(newSongs):
    appleMusicPath = (
        "Users/"
        + getpass.getuser()
        + "/Music/Media.localized/Automatically Add to Music.localized"
    )
    print(newSongs)
    for file in newSongs:
        # shutil.copyfile(file, appleMusicPath)
        print(subprocess.getoutput("cp" + " " + file + " " + appleMusicPath))


def main():
    url = input("Enter playlist or video url: ")
    newSongs = download(url)
    # if newSongs:
    #     addToAppleMusic(newSongs)


if __name__ == "__main__":
    main()

"""
TODO:
# set genre & album to playlist manually and set default
# add to apple music
# add to playlist option for single songs and whole playlists with apple music api
# maybe add youtube api to automatically sync playlists
"""
