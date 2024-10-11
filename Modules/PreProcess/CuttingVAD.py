import json
import os
from os import path
from tqdm import auto as tqdm
from moviepy.editor import AudioFileClip
from Modules.SileroVAD import timestamps_dict_to_tuple


def read_speech_timestamps(speech_timestamps_path: str) -> list[dict]:
    with open(speech_timestamps_path, "r") as f:
        return json.loads(f.read())


def audio_timestamp_nameing(timestamp: tuple[float | int]) -> str:
    start, end = timestamp
    return f"{start},{end}.wav"


def is_audio_exist(folder: str, timestamp: tuple[float | int]) -> bool:
    audio_name = audio_timestamp_nameing(timestamp)
    audio_path = path.join(folder, audio_name)
    return path.exists(audio_path)


def invoke(
    folder: str,
    timestamps_path: str,
    audio_path: str,
    exist_ok=True,
    visible=True,
) -> None:
    if exist_ok and path.exists(folder):
        return

    os.makedirs(folder)
    audio = AudioFileClip(audio_path)

    timestamps_dicts = read_speech_timestamps(timestamps_path)
    timestamps = timestamps_dict_to_tuple(timestamps_dicts)

    for stamp in tqdm.tqdm(timestamps, disable=(not visible)):
        clip_path = path.join(folder, audio_timestamp_nameing(stamp))
        audio.subclip(*stamp).write_audiofile(clip_path, logger=None)
