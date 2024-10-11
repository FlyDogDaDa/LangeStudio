import json
from os import path
from Modules.Converter import Time
from Modules.PreProcess.CuttingVAD import (
    read_speech_timestamps,
)


def invoke(
    transcription_path: str,
    timestamps_path: str,
    subtitle_path: str,
) -> None:

    timestamps = read_speech_timestamps(timestamps_path)

    with open(transcription_path, encoding="utf-8") as f:
        transcriptions = json.loads(f.read())

    words = Time.whisper_to_global_word_timestamps(timestamps, transcriptions)

    with open(subtitle_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(words, ensure_ascii=False))
