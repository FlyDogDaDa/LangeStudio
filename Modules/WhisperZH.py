import os
import json
import torch
import whisper


def load_model(name="large-v2", download_root="whisper_models") -> whisper.Whisper:
    device = "cuda" if torch.cuda.is_available() else "cpu"  # 嘗試使用GPU
    # 讀取並回傳whisper模型
    return whisper.load_model(name=name, device=device, download_root=download_root)


def invoke(audio_path: str, model: whisper.Whisper, config) -> list[dict]:
    result = model.transcribe(audio_path, **config)
    return result["segments"]
