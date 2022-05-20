import yt_dlp
from ydl_opts import ydl_opts
import os


class ytDownload:

    # ydl_opts = ydl_opts

    def __init__(self, url, path="/Users/tilschulz/Music/dj/ytdl"):
        self.path = path
        self.url = url
        ydl_opts["paths"] = {"home": self.path}
        ydl_opts["download_archive"] = self.path + "/" + "history.txt"

    def handleDownload(self):
        if "playlist" in self.url:
            return self.handlePlaylist(self.url)
        else:
            self.handleSong(self.url)

    def handleSong(self):
        ydl_opts["extract_flat"] = False  # do not resolve URLs, return the immediate result.
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                self.url,
                download=False,
            )
            if info:  # if it was downloaded already, info object is None
                self.downloadSong(ydl, info, self.url, self.path)

    def handlePlaylist(self):
        ydl_opts["noplaylist"] = False  # download playlist instead of single video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            infoPlaylist = ydl.extract_info(
                self.url,
                download=False,
            )
            entries = infoPlaylist["entries"]
            print("Playlist ID:", infoPlaylist["id"])
            print("Total playlist videos:", infoPlaylist["playlist_count"])  # amount of all playlist videos
            print("Videos to be downloaded:", len(entries))  # amount of videos not downloaded yet
            self.downloadPlaylist(ydl, entries)
        self.removePlaylistThumbnail(PlaylistTitle=infoPlaylist["title"])
        print("Successfully downloaded playlist!")

    def downloadPlaylist(self, ydl, entries):
        leftovers = []
        newSongPaths = []
        vidCounter = 1
        for entry in entries:
            if not entry:
                print("Can't get information on video {} - download next video!".format(entry))
            else:
                songURL = entry["url"]
                info = ydl.extract_info(songURL, download=False)
                print("Download Song {}/{} ...".format(vidCounter, len(entries)))
                postData = self.downloadSong(ydl, songURL, info)
                # print(postData)
                if not postData[0]:
                    leftovers.append(postData[1])
                elif not postData[1]:
                    newSongPaths.append(postData[0])
            vidCounter += 1
        if leftovers != []:
            print("Videos not downloaded because they didn't match song pattern: ", leftovers)
        # return newSongPaths

    # TODO: continue with postData

    def downloadSong(self, ydl, info, url, downloadAll=False):
        def rename():
            newFilePath = self.path + "/" + artistTrack[0] + " - " + artistTrack[1] + ".mp3"
            os.rename(mp3Path, newFilePath)
            return newFilePath

        def isSongPattern():
            if metaData and (duration <= 900):  # Asumption: Track is not longer than 15 min = 900 sec
                return True
            elif not metaData and info.get(
                "track", False
            ):  # YT song pattern - just the song is the title, track is provided though
                return True
            return False

        title = info["title"]
        renameFile = False
        if not "-" in title:  # change filename later to be format 'artist - track' instead of just 'track'
            renameFile = True
        duration = info["duration"]
        metaData = extractSongMetaData(title)  # song pattern recognition
        mp3Path = path + "/" + title + ".mp3"
        if isSongPattern():  # metadata was extracted and was not provided by url --> set metadata
            ydl.download([url])
            artistTrack = handleSongMetaData(metaData, info, mp3Path)
            if renameFile:
                mp3Path = rename()
            return (mp3Path, None)
        else:
            if not downloadAll:
                print(emoji.emojize(":cross_mark: Could not identify a song pattern for video '{}'").format(title))
                print("Download just songs, skip video!")
            else:
                print("Download audio of video '{}'".format(title))
                ydl.download([url])
                # yt_dlp sets title as track & uploader as artist per default
                # handleOtherMetaData(mp3Path)
            return (None, (url, title))

    def removePlaylistThumbnail(self, PlaylistTitle):
        os.remove(self.path + "/" + PlaylistTitle + ".jpg")
