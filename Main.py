import os
import google.generativeai as genai
import moviepy.audio

genai.configure(api_key=os.getenv("google_ai_studio_api_key"))  # 設定KEY
assert __name__ == "__main__", ImportError("此為主程式，請勿引用此模組!!")

import json
import time
from opencc import OpenCC
from FileData.FileManager import AutoFileCache
from Character.CharacterManager import get_character, ChatWrapper, ContentFactory
from Character.CharacterManager import ContentFactory as CF
from google.generativeai.generative_models import _MODEL_ROLE, _USER_ROLE


zhTW_CC = OpenCC("s2twp")  # 取用中文轉換器
file = AutoFileCache.get_file("Character\\Naledge\\檢討.txt")
lange = get_character("Lange")
lange_chat = ChatWrapper(lange)
# lange_chat.append(file)

import time
import gradio as gr
from gtts import gTTS

# Language we want to use
language = "zh-tw"
TTS_path = "swarp\\TTS_audio.mp3"


with gr.Blocks() as demo:
    audio = gr.Audio()
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message: str, chat_history: list, audio):
        lange_chat.append(message)  # 加入使用者訊息
        response = lange_chat.invoke()  # 呼叫模型
        bot_message = zhTW_CC.convert(response.text)  # 轉成繁體
        chat_history.append((message, bot_message))
        gTTS(text=bot_message, lang=language, slow=False).save(TTS_path)
        audio = gr.Audio(
            TTS_path,
            sources=[],
            autoplay=True,
            editable=False,
        )  # TODO:語音太慢

        return "", chat_history, audio

    msg.submit(respond, [msg, chatbot, audio], [msg, chatbot, audio])

if __name__ == "__main__":
    demo.launch(inbrowser=True)

# user_name = "Kwene"
# while True:
#     user_input = input(f"\n{user_name}：")
#     if user_input.lower() == "q":
#         break
#     lange_chat.append(f"{user_name}：{user_input}")  # 串接使用者訊息
#     response = lange_chat.invoke()  # 呼叫模型
#     reply = zhTW_CC.convert(response.text)  # 轉成繁體
#     print("Lange：", reply, sep="")


history_str = json.dumps(
    tuple(genai.protos.Content.to_dict(message) for message in lange_chat.history),
    ensure_ascii=False,
)
with open(f"History\\對話紀錄_{int(time.time())}.json", "w", encoding="utf-8") as f:
    f.write(history_str)
