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
            "preferredcodec": "mp3",  # change to flac if preferred
            "preferredquality": "320",
        },
        {
            "key": "FFmpegMetadata",
            "add_metadata": True,
        },
        {"key": "EmbedThumbnail"},  # embed thumbnail
    ],
}
