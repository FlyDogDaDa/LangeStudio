import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image

P = 4
scale_factor = 4
# 設定雜訊尺寸和放大倍率
noise_size = (1920 // P, 1080 // P)

# 生成高斯雜訊
noise = (((torch.randn(1, 1, *noise_size) + 0.5) / 2) * 255).to(torch.uint8)

# 雙線性插值放大
noise: torch.Tensor = F.interpolate(
    noise,
    scale_factor=scale_factor,
    mode="bilinear",
    align_corners=False,
)
noise = noise.squeeze(0).repeat_interleave(3, 0).permute(2, 1, 0)
noise_array = noise.numpy()
# 轉換為 PIL Image 並儲存
pil_img = Image.fromarray(noise_array)

pil_img.save(f"gaussian_noise_{P}p.png")
