class metaData:
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
                print("Error: yt_dlp extracted different filename. Keep default yt_dlp metadata instead")

        def setAlbumAndGenre():
            try:
                audio = EasyID3(mp3Path)
                audio["album"] = "ytdl"
                audio["genre"] = "Techno"
                audio.save()
            except (FileNotFoundError, mutagen.MutagenError) as e:
                print("Error: yt_dlp extracted different filename. Keep default yt_dlp metadata instead")

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
