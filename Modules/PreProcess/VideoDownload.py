from pytubefix import YouTube
from pytubefix.cli import on_progress
from os import path


def read_name_cache(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()  # 讀名稱快取


def write_name_cache(path: str, name: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        return f.write(name)  # 讀名稱快取


class yt_obj_singleton:
    def __init__(self, url: str) -> None:
        self.yt = None  # 初始影片未得到
        self.url = url

    def get_youtube(self) -> YouTube:
        if self.yt is None:
            self.yt = YouTube(self.url, on_progress_callback=on_progress)
        return self.yt


def download(url: str, folder: str, name: str, exist_ok=True) -> str:
    "Download the video of `url` to `folder` and return the file path."
    video_path = path.join(folder, name)
    if path.exists(video_path):
        return video_path

    yt = YouTube(url, on_progress_callback=on_progress)
    ys = yt.streams.get_highest_resolution()
    ys.download(folder, name, skip_existing=exist_ok)
    return video_path
