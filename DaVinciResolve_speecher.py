assert __name__ == "__main__", RuntimeError(
    "This program can only be executed as the main program"
)
import os
import json
from os import path
from Modules.PreProcess import VideoAudioSplit, DetectVAD
from pywinauto import application
from moviepy.editor import VideoFileClip
import win32con

# auto_delete = True  # TODO:實作 # TODO:改成設定


def seconds_to_timecode(seconds: float, fps: int) -> str:
    """將秒數轉換成 timecode

    Args:
      seconds: 秒數
      fps: 格率 (frames per second)

    Returns:
      str: timecode 格式的字串
    """

    total_frames = int(seconds * fps)
    hours = total_frames // (fps * 60 * 60)
    minutes = (total_frames // (fps * 60)) % 60
    seconds = (total_frames // fps) % 60
    frames = total_frames % fps

    return f"{hours:02d}{minutes:02d}{seconds:02d}{frames:02d}"


class WindowOperator:
    def __init__(self) -> None:
        # 連接到 Resolve.exe 應用程式
        self.app = application.Application().connect(path="Resolve.exe")

        # 獲取所有對話方塊（通常啟動視窗會是對話方塊）
        self.dlg = self.app.window(title_re="DaVinci Resolve.*")
        self.keyboard_buffer = []

    def add_key(self, key: str):
        self.keyboard_buffer.append(key)  # 添加指令

    def submit(self, clear_buffer: bool = True):
        # command = "".join(self.keyboard_buffer)  # 合併指令
        for k in self.keyboard_buffer:
            self.dlg.type_keys(k, set_foreground=True)  # 運行指令
        if clear_buffer:  # 需要清除
            self.keyboard_buffer.clear()  # 清除暫存


def do_blade_time(window: WindowOperator, time: float) -> None:
    # ^B 代表 Ctrl+B 鍵
    # %X 代表 ALT+X 鍵
    timecode = seconds_to_timecode(time, fps)
    window.add_key(timecode)
    window.add_key("{ENTER}")
    window.add_key("^B")


window = WindowOperator()

with open(path.join("Modules", "config.json"), encoding="utf-8") as f:
    config = json.load(f)

# 建立swarp資料夾
root = "swarp"
os.makedirs(root, exist_ok=True)

# 使用者輸入路徑
video_path = "404NotFind\n"  # 設為空#"D:\\Documents\\Desktop\\GitHubs\\LangeStudio\\swarp\\original_input.mp4"
while not path.exists(video_path):  # 路徑不存在
    video_path = input("(Ctrl+C強制關閉) 請輸入影片完整路徑：")
    video_path = video_path.replace('"', "").strip()  # 字串清理

# 取得影片 FPS
fps = int(VideoFileClip(video_path).fps)

# 分割影片檔案
audio_path = path.join(root, "audio.wav")
VideoAudioSplit.audio(video_path, audio_path, config["audio"])

# 創建VAD時間戳
speech_timestamps_path = path.join(root, "speech_timestamps.json")
DetectVAD.invoke(speech_timestamps_path, audio_path, config["SileroVAD"])


with open(speech_timestamps_path) as f:
    timestamps = json.load(f)

window.add_key("^4")  # 切到時間軌道
window.add_key("+V")  # 選取整個片段
window.add_key("{VK_MENU down}{UP}{VK_MENU up}")  # 軌道上移

for t in timestamps:
    do_blade_time(window, t["start"])
    window.add_key("+V")
    do_blade_time(window, t["end"])
    window.add_key("^4")  # 切到時間軌道
    window.add_key("{VK_MENU down}{DOWN}{VK_MENU up}")  # 軌道下移
window.submit()


# os.remove(audio_path)
# os.remove(speech_timestamps_path)

# D:\Documents\Desktop\GitHubs\LangeStudio\swarp\original_input.mp4

# 達芬奇專案的編輯檔案資料庫
# C:\Users\Home\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Resolve Project Library\Resolve Projects\Users\guest\Projects\自動剪輯測試
