import logging

from PIL import Image
from moviepy.editor import VideoClip
from typing import Iterable, Generator

# import numpy as np


class Moviepy:
    @staticmethod
    def iter_PILs_from_clip(video: VideoClip) -> Generator[Image.Image, None, None]:
        return (Image.fromarray(arry) for arry in video.iter_frames())

    @staticmethod
    def get_PIL_from_clip(video: VideoClip, second: float) -> Image.Image:
        if isinstance(second, Iterable):  # 如果傳入一個可迭代物件
            logging.warning("please use `get_batch_PIL_from_clip` for iterable seconds")
            return Moviepy.get_batch_PIL_from_clip(video, second)  # 呼叫迭代取得方法

        arry = video.get_frame(second)
        image = Image.fromarray(arry)
        return image

    @staticmethod
    def get_batch_PIL_from_clip(
        video: VideoClip, seconds: Iterable[float]
    ) -> tuple[Image.Image]:
        if not isinstance(seconds, Iterable):  # 如果非可迭代物件
            raise TypeError("Seconds must be an iterable")

        return tuple(Moviepy.get_PIL_from_clip(video, second) for second in seconds)


class Time:
    @staticmethod
    def frequency_to_ratio(frequency):
        return 1 / frequency

    @staticmethod
    def ratio_to_frequency(ratio):
        return 1 / ratio

    @staticmethod
    def timestamps_local_to_global(global_stamp: dict, local_stamp: dict) -> dict:
        end = global_stamp["end"]
        start = global_stamp["start"]
        return {
            "start": max(start + local_stamp["start"], start),
            "end": min(start + local_stamp["end"], end),
        }

    @staticmethod
    def whisper_to_global_word_timestamps(
        global_stamp: list[dict], local_stamp: list[dict[str, list[dict]]]
    ) -> list[dict]:
        if len(global_stamp) != len(local_stamp):
            raise ValueError("兩 stamp 長度不相等")
        timestamps = []
        for g_stamp, l_stamps in zip(global_stamp, local_stamp):
            for l_stamp in l_stamps:
                for word in l_stamp["words"]:
                    stamp = Time.timestamps_local_to_global(g_stamp, word)
                    stamp["word"] = word["word"]
                    timestamps.append(stamp)

        return timestamps
