import torch
from torchvision import io as tvio
from tqdm import auto as tqdm
from Modules import CLIP
from moviepy.editor import VideoFileClip, VideoClip
from os import path
import time

# TODO:模模化

vision_path = "swarp\\vision.webm"
vision, audio, fps_dict = tvio.read_video(vision_path, output_format="TCHW")
# TODO: 加速純vision讀取
del audio, fps_dict


# vision.size(0)是幀數量
chunk_amount = vision.size(0) // (FPS * 3)
vision_chunk_emb = []
for chunk in tqdm.tqdm(vision.chunk(chunk_amount)):
    chunk = chunk.to(torch.half) / 256
    emb = CLIP.images_encode(chunk)
    vision_chunk_emb.append(emb)
vision_emb = torch.cat(vision_chunk_emb)

torch.save(vision_emb, "swarp\\vision_emb.pt")
