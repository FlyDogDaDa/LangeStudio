import json
import torch
from os import path
from tqdm import auto as tqdm
from faster_whisper import WhisperModel
from Modules.PreProcess.CuttingVAD import (
    read_speech_timestamps,
    timestamps_dict_to_tuple,
)

# device = "cuda" if torch.cuda.is_available() else "cpu"

model = WhisperModel("arc-r/faster-whisper-large-zh-cv11")
prompt = "以下是一段國語錄音的字幕："
segments, info = model.transcribe(
    "swarp\\speech_clips\\154.2,166.5.wav",
    language="zh",
    condition_on_previous_text=False,
    initial_prompt=prompt,
)
a = []
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    a.append({"start": segment.start, "end": segment.end, "text": segment.text})

with open("test.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(a, ensure_ascii=False))


def invoke(
    transcription_path: str,
    timestamps_path: str,
    audio_path: str,
    exist_ok=True,
    visible=True,
) -> None:
    if exist_ok and path.exists(transcription_path):
        return

    transcriptions = []
    timestamps_dicts = read_speech_timestamps(timestamps_path)
    for i, timestamps in tqdm.tqdm(enumerate(timestamps_dicts), disable=(not visible)):
        for segment in segments:
            transcriptions.append(
                {
                    "start": timestamps["start"] + segment.start,
                    "end": timestamps["start"] + segment.end,
                    "text": segment.text,
                    "index": i,
                }
            )
        segment.words
        scripts = []
        transcriptions.append(scripts)
