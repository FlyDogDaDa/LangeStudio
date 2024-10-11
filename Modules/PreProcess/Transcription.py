import json
from os import path
from tqdm import auto as tqdm
from Modules import WhisperZH
from Modules.PreProcess.CuttingVAD import (
    read_speech_timestamps,
    timestamps_dict_to_tuple,
    audio_timestamp_nameing,
)


def invoke(
    transcription_path: str,
    timestamps_path: str,
    audio_folder: str,
    config,
    exist_ok=True,
    visible=True,
) -> None:
    if exist_ok and path.exists(transcription_path):
        return

    timestamps_dicts = read_speech_timestamps(timestamps_path)
    timestamps = timestamps_dict_to_tuple(timestamps_dicts)

    modle = WhisperZH.load_model()
    transcriptions = []
    for stamp in tqdm.tqdm(timestamps, disable=(not visible)):
        audio_path = path.join(audio_folder, audio_timestamp_nameing(stamp))
        segments = WhisperZH.invoke(audio_path, modle, config)
        transcriptions.append(segments)

    with open(transcription_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(transcriptions, ensure_ascii=False))
