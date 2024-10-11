import os
import csv
import google.generativeai as genai
import warnings

from google.api_core.exceptions import PermissionDenied, ResourceExhausted
from tqdm import tqdm
from Character import CharacterManager
from typing import Iterable, Generator, Callable
from time import time, sleep


def name_bar(datas: Iterable, key: Callable[..., str]) -> Generator:
    tqdm_obj = tqdm(total=len(datas))
    for data in datas:
        name = key(data)
        tqdm_obj.desc = name
        tqdm_obj.refresh()
        yield data
        tqdm_obj.update()


"""
def cool_down_iter(datas: Iterable, top_speed: float) -> Generator:
    remaining = None
    for data in datas:
        if not (remaining is None):
            sleep(remaining)
        start_time = time()
        yield data
        end_time = time()
        remaining = top_speed - (end_time - start_time)
"""


class Timer:
    def __init__(self, time: float) -> None:
        self.time = time
        self.start_time = None
        self.end_time = None

    def start(self) -> None:
        self.start_time = time()

    def end(self) -> None:
        self.end_time = time()

    def block(self, warning: bool = True) -> None:
        if (self.end_time is None) or (self.start_time is None):
            if warning:
                warnings.warn(
                    "User warning: start_time or end_time is None, please call `start` and `end` before using `block()`"
                )
            return
        remaining = self.time - (self.end_time - self.start_time)
        if remaining > 0:
            sleep(remaining)


def translate(
    model: genai.GenerativeModel,
    file_data: genai.types.FileDataType,
    language_tags: list[list[str]],
    save_folder: str,
    cool_down: float = 0,
):
    template = "(補充資訊：1. **崑霓**的英文名是**Kwenen**，若出現請盡量使用__Kwenen__，牠是一名Vtuber。)\n"
    template += "(備註：1. 你的答覆文字將會直接寫入到.svb檔案，僅輸出內容，無須答覆；無須markdown。\t"
    template += "2. 無法翻譯的專有名詞則保留原始用詞)\n"
    template += "以下附件是該影片的`.sbv` file，請你將其翻譯成{0}(`{1}`)：\n"

    # 請求傳送計時器：請求冷卻
    clock = Timer(cool_down)
    # 裝飾器：以language_tw作為進度條顯示名子
    bar = name_bar(language_tags, lambda x: x[2])
    for language_code, language_en, language_tw in bar:
        # 輸出檔案路徑
        path = os.path.join(save_folder, language_tw + ".sbv")
        # 檔案已存在
        if os.path.exists(path):
            continue  # 跳過
        # 格式化提示詞：填充目標語言
        prompt = template.format(language_tw, language_code)
        # 阻擋過快的請求：當有需要生成
        clock.block(warning=False)
        # 計時開始
        clock.start()
        # 生成翻譯字幕
        response = model.generate_content([prompt, file_data])
        # 寫入字幕檔案
        with open(path, "w", encoding="utf-8") as f:
            f.write(response.text)
        # 計時結束
        clock.end()


def main(captions_path: genai.types.FileDataType, video_name: str):
    genai.configure(api_key=os.getenv("google_ai_studio_api_key"))  # 設定KEY
    character_save_folder = os.getenv("character_save_folder")
    captions_save_folder = os.getenv("captions_save_folder")

    captions_save_folder = os.path.join(captions_save_folder, video_name)
    os.makedirs(captions_save_folder, exist_ok=True)

    model_name = "SBV_Translator"
    character_save_folder = os.path.join(character_save_folder, model_name)
    model = CharacterManager.creat_character(model_name)

    language_tags_name = "Commonly used IETF language tags.csv"
    language_tags_path = os.path.join(character_save_folder, language_tags_name)
    with open(language_tags_path, encoding="utf-8") as f:
        iter = csv.reader(f)
        next(iter)  # `pop(0)`移除標題
        language_tags = list(iter)

    # TODO:將路徑改到swarp
    file_name, file_ex = os.path.splitext(os.path.basename(captions_path))
    file_name = str.lower(file_name)

    try:
        captions_file_data = genai.get_file(file_name)
    except PermissionDenied:
        captions_file_data = genai.upload_file(
            captions_path,
            mime_type="text/plain",
            name=file_name,
        )

    translate(model, captions_file_data, language_tags, captions_save_folder, 31)


if __name__ == "__main__":
    main("Captions\\CrafterPanel\\zh-tw-CrafterPanel.sbv", "CrafterPanel")
