import os
import json
import google.generativeai as genai
from google.generativeai import types
from typing import Iterable, Any, Literal

from google.generativeai.types import content_types
from google.generativeai.protos import Content, Part
from google.generativeai.generative_models import _MODEL_ROLE


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


class ChatWrapper:
    def __init__(
        self,
        model: genai.GenerativeModel,
        history: Iterable[content_types.StrictContentType] | None = None,
        tools: content_types.FunctionLibraryType | None = None,
        tool_config: content_types.ToolConfigType | None = None,
        enable_automatic_function_calling: bool = False,
    ) -> None:
        self.model = model
        self.history = list(history) if history is not None else list()
        self.do_function_calling = enable_automatic_function_calling
        self.tools = tools
        self.tool_config = tool_config

    def get_history(self) -> list:
        return self.history

    def append(self, content: content_types.ContentType) -> None:
        self.history.append(content)

    def invoke(self) -> genai.types.GenerateContentResponse:
        response = self.model.generate_content(
            self.history,
            tools=self.tools,
            tool_config=self.tool_config,
        )
        return response


def start_chat_with(
    name: str,
    history: Iterable[types.StrictContentType] | None = None,
    enable_automatic_function_calling: bool = False,
) -> genai.ChatSession:
    return get_character(name).start_chat(
        history=history,
        enable_automatic_function_calling=enable_automatic_function_calling,
    )


class ContentFactory:
    def model_text(text: str) -> genai.types.ContentType:
        return Content(parts=[Part(text=text)], role=_MODEL_ROLE)


# class PartFactory:
#     @staticmethod
#     def text(parts=[genai.protos.Part(text="此為`記憶.md`檔案。請接收此檔案<記憶.md>")],
#         role=_USER_ROLE,)

# class ChatSession:
#     def __init__(
#         self,
#         model: genai.GenerativeModel,
#         history: Iterable[types.StrictContentType] | None = None,
#         tools: genai.types.FunctionLibraryType | None = None,
#         setting: genai.protos.ToolConfig | None = None,
#     ) -> None:
#         self.model = model
#         self.history = list(history)
#         self.tools = tools
#         self.setting = setting

#     def set_tools(self, tools: genai.types.FunctionLibraryType):
#         self.tools = tools

#     def set_tools_setting(self, setting: genai.protos.ToolConfig):
#         self.setting = setting

#     def send(self, content: genai.types.ContentType) -> None:
#         self.history.append(content)

#     def invoke(self) -> genai.types.ChatResponse:
#         contents = content_types.to_contents(self.history)
#         return self.model.generate_content(contents)


# def start_chat_with(
#     name: str,
#     history: Iterable[types.StrictContentType] | None = None,
#     tools: genai.types.FunctionLibraryType | None = None,
#     setting: genai.protos.ToolConfig | None = None,
# ) -> ChatSession:
#     return ChatSession(get_character(name), history, tools, setting)
