from io import BytesIO
import time
import wave
import pyaudio
import torch


from queue import Queue
from silero_vad import load_silero_vad, get_speech_timestamps

# # Example using colorama to print colored text in Python
# import colorama
# from colorama import Fore, Style

# colorama.init(autoreset=True)  # Initializes colorama and autoresets color


torch.set_grad_enabled(False)  # 關閉梯度
device_index = 0
CHUNK = 512  # 每幀音訊樣本數
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 8000 or 16000
RECORD_SECONDS = 5
BAR_LEN = 50
threshold = 0.5
silent_frame = 50
frame_buffer = 20
log_frame = 2  # 必須大於零
pyAudio = pyaudio.PyAudio()
stream = pyAudio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=device_index,
    # frames_per_buffer=CHUNK,
)
model = load_silero_vad(onnx=False)


def get_buffer(buffer: Queue) -> list:
    items = []
    while not buffer.empty():
        items.append(buffer.get())
    return items


def read_mic() -> bytes:
    return stream.read(CHUNK)  # 讀麥克風


def get_activate(data: bytes) -> float:
    wav = torch.frombuffer(data, dtype=torch.int16).to(torch.float32) / 256
    return model(wav, RATE).item()


def bytes_to_wav_link(data: bytes) -> None:
    memory = BytesIO()
    with wave.open(memory, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyAudio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(data)
    memory.seek(0)
    return memory


def save_audio(path: str, data: BytesIO) -> None:
    with open(path, "wb") as wf:
        wf.write(data.read())


class vertical_bar:
    pass


def main():
    buffer = Queue(maxsize=frame_buffer)

    frames = []
    silent_counter = silent_frame
    log_counter = 0
    recording = False
    is_active = True
    stream.start_stream()
    print("開始錄製!")
    while True:
        data = read_mic()
        activate = get_activate(data)
        is_active = activate > threshold

        if not is_active:  # 有聲音
            silent_counter -= 1
        else:
            recording = True
            silent_counter = silent_frame

        if recording:
            frames.append(data)
        else:
            if buffer.full():  # 緩衝滿了
                buffer.get()  # 刪除最舊
            buffer.put(data)  # 存入資料

        if recording and silent_counter == 0:
            recording = False
            output_path = f"聲音輸出測試\\{int(time.time())}.wav"
            data = b"".join(get_buffer(buffer) + frames[: -silent_frame + frame_buffer])
            wav_bytes = bytes_to_wav_link(data)
            save_audio(output_path, wav_bytes)
            frames.clear()

        if log_counter:
            log_counter -= 1
        else:
            log_counter = log_frame

            print(
                "Mic|",
                "█" * int(BAR_LEN * activate),
                " " * int(BAR_LEN - BAR_LEN * activate),
                "|",
                "R" if recording else "—",
                sep="",
                end="\r",
            )


def exit_handler():
    stream.stop_stream()
    stream.close()
    pyAudio.terminate()
    print("\n鍵盤終止事件：錄音程式(VAD)已停止運作。\n")


# TODO:將錄音程式物件化
# TODO:退出自動關閉串流
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit_handler()
