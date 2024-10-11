from silero_vad import load_silero_vad, read_audio, get_speech_timestamps


def timestamps_dict_to_tuple(
    timestamps: list[dict[str:float]],
) -> list[tuple[float, float]]:
    return [tuple(dic.values()) for dic in timestamps]


def invoke_one_time(audio_path: str, config: dict) -> list[dict[str, float | int]]:
    model = load_silero_vad()
    wav = read_audio(audio_path)  # backend (sox, soundfile, or ffmpeg) required!
    return get_speech_timestamps(wav, model, **config)
