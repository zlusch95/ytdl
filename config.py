from dataclasses import dataclass
from dataclasses import field
from typing import ClassVar, List


@dataclass
class YdlpConfig:
    # post processors
    ffmpeg_extractaudio_pp: ClassVar[dict] = {
        "key": "FFmpegExtractAudio",
        "preferredcodec": "flac",  # mp3, flac (works with soundcloud and yt)
        "preferredquality": "320",
    }
    ffmpge_metadata_pp: ClassVar[dict] = {
        "key": "FFmpegMetadata",
        "add_metadata": True,
    }
    embedd_thumbnail_pp: ClassVar[dict] = (
        {"key": "EmbedThumbnail"},
    )  # embed thumbnail

    # config options
    paths: dict = field(default={})
    download_archive: str = field(default="")
    extract_flat: bool = field(default=True)
    ignoreerrors: bool = field(default=True)
    outtmpl: dict = field(default={"default": "%(title)s.%(ext)s"})
    format: str = field(default="bestaudio/best")
    noplaylist: bool = field(default=True)
    writethumbnail: bool = field(default=True)
    restrictfilenames: bool = field(default=False)
    postprocessors: List[dict] = field(
        default=[ffmpeg_extractaudio_pp, ffmpge_metadata_pp, embedd_thumbnail_pp]
    )


# user agent for meta data extraction
user_agent: tuple = (
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
)
