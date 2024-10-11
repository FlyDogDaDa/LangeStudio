from os import path
from PIL import Image as pil
from pkg_resources import parse_version
from moviepy.editor import VideoFileClip, AudioFileClip, VideoClip, AudioClip

if parse_version(pil.__version__) >= parse_version("10.0.0"):
    pil.ANTIALIAS = pil.LANCZOS  # resize方法補釘


# 讀取速度webm:6.194222450256348 #檔案較大 #轉檔較慢
# 讀取速度mp4: 6.706133842468262 #檔案較小 #轉檔較快
def vision(
    video_path: str,
    output_path: str,
    config: dict,
    exist_ok=True,
) -> None:
    if exist_ok and path.exists(output_path):
        return
    video = VideoFileClip(video_path)
    video.write_videofile(output_path, audio=False, **config)


def audio(
    video_path: str,
    output_path: str,
    config: dict,
    exist_ok=True,
) -> None:
    if exist_ok and path.exists(output_path):
        return
    audio = AudioFileClip(video_path)
    audio.write_audiofile(output_path, **config)
