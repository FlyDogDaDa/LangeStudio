import os
from uuid import uuid1
import time
import google.generativeai as genai
from google.generativeai.protos import Content, Part, File
from google.generativeai.types import content_types

root_folder = os.getenv("fileData_save_folder")
if not os.path.exists(root_folder):
    raise FileNotFoundError(f"找不到此資料夾位置:{root_folder}")


class AutoFileCache:
    """
    file:
        display_name = file_path
        name = UUID

    path2id_dict:
        key: path
        value: UUID
    """

    path2file_dict = dict((file.display_name, file) for file in genai.list_files())

    @staticmethod
    def get_uuid() -> str:
        return str(uuid1())

    @classmethod
    def have_file(cls, path: str) -> bool:
        return path in cls.path2file_dict  # 路徑已經存在

    @classmethod
    def upload_file(cls, path: str) -> File:
        uuid = cls.get_uuid()  # 生成UUID
        file = genai.upload_file(path, name=uuid, display_name=path)  # 上傳檔案
        cls.path2file_dict[path] = file  # 紀錄UUID
        return file  # 回傳檔案

    @classmethod
    def delete_file(cls, path: str) -> None:
        file = cls.path2file_dict.get(path)
        genai.delete_file(file)  # 刪除檔案
        del cls.path2file_dict[path]  # 從dict中移除

    @classmethod
    def get_file(cls, path: str) -> File:
        if cls.have_file(path):  # 有檔案
            return cls.path2file_dict[path]  # 回傳檔案並早退
        return cls.upload_file(path)  # 上傳檔案並回傳檔案


if __name__ == "__main__":  # debugging purposes
    genai.configure(api_key=os.getenv("google_ai_studio_api_key"))  # 設定KEY
    file = AutoFileCache.get_file("Character\\Naledge\\檢討.txt")
    print(file)
