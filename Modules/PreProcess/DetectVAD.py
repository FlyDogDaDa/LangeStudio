import json
from os import path
from Modules import SileroVAD


def invoke(
    speech_timestamps_path: str,
    audio_path: str,
    config,
    exist_ok=True,
) -> None:
    if exist_ok and path.exists(speech_timestamps_path):
        return

    speech_timestamps = SileroVAD.invoke_one_time(audio_path, config)
    with open(speech_timestamps_path, "w") as f:
        f.write(json.dumps(speech_timestamps))
