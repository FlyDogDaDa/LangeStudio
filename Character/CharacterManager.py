import os
import json
import google.generativeai as genai
from google.generativeai import types
from typing import Iterable


root_folder = os.getenv("character_save_folder")

if not os.path.exists(root_folder):
    raise FileNotFoundError(f"找不到此資料夾位置:{root_folder}")


characters_dict: dict[str : genai.GenerativeModel] = {}


def read_character_json(name: str) -> dict:
    path = os.path.join(root_folder, name, name + ".json")

    if not os.path.exists(path):
        raise FileNotFoundError(f"嘗試讀取路徑:{path}\n此路徑不存在")

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def creat_character(name: str) -> genai.GenerativeModel:
    setting = read_character_json(name)
    runSettings = setting["runSettings"]
    systemInstruction = setting["systemInstruction"].get("text")

    generationConfig = types.GenerationConfig(
        runSettings["candidateCount"],
        None,
        runSettings["maxOutputTokens"],
        runSettings["temperature"],
        runSettings["topP"],
        runSettings["topK"],
    )
    model = genai.GenerativeModel(
        runSettings["model"],
        runSettings["safetySettings"],
        generationConfig,
        None,
        None,
        systemInstruction,
    )

    return model


def get_character(name: str) -> genai.GenerativeModel:
    "singleton of character GenerativeModel"
    if name not in characters_dict:
        model = creat_character(name)
        characters_dict[name] = model
    return characters_dict[name]


def start_chat_with(
    name: str,
    history: Iterable[types.StrictContentType] | None = None,
    enable_automatic_function_calling: bool = False,
) -> genai.ChatSession:
    return get_character(name).start_chat(
        history=history,
        enable_automatic_function_calling=enable_automatic_function_calling,
    )
