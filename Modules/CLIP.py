import clip
import torch
from torch import Tensor
from torch.nn import functional as nnF
from torchvision.transforms import (
    Compose,
    Resize,
    CenterCrop,
    Normalize,
    InterpolationMode,
)
from torchvision.transforms import functional as tfF
from PIL import Image
from typing import Iterable

torch.set_grad_enabled(False)  # 關閉梯度計算


def transform(n_px):  # 複製clip._transform()
    return Compose(
        [
            # Resize(n_px, interpolation=InterpolationMode.BICUBIC),
            CenterCrop(n_px),
            Normalize(
                (0.48145466, 0.4578275, 0.40821073),
                (0.26862954, 0.26130258, 0.27577711),
            ),
        ]
    )


device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
preprocess = transform(model.visual.input_resolution)

# cosine similarity as logits
logit_scale = model.logit_scale.exp()


def images_encode(images: Iterable[Image.Image]) -> Tensor:
    images = preprocess(images)
    image_features = model.encode_image(images)
    # normalized features
    image_features = image_features / image_features.norm(dim=1, keepdim=True)
    return image_features


def __images_encode(images: Iterable[Image.Image]) -> Tensor:
    # TODO: 張量圖片批量輸入
    image = torch.stack(tuple(preprocess(img) for img in images)).to(device)
    image_features = model.encode_image(image)
    # normalized features
    image_features = image_features / image_features.norm(dim=1, keepdim=True)
    return image_features


def similarity(A: Tensor, B: Tensor) -> Tensor:
    return logit_scale * A @ B.t()


def get_max_change_index(sequence: Tensor) -> int:
    return sequence.diff().abs().argmax()


# contents: VideoClip, elements: VideoClip, threshold: float, check_frequency: int
def find_element_change_index(
    contents: Tensor, features: Tensor, average_kernel: int
) -> int:
    pad, r = divmod(average_kernel - 1, 2)
    if r != 0:
        raise ValueError("`average_kernel` must be a multiple of two")

    score = similarity(contents, features).amax(-1)
    score_smooth = nnF.avg_pool1d(score.unsqueeze(0), average_kernel, 1, pad).squeeze(0)
    return get_max_change_index(score_smooth)


def dropping_frames(index: Tensor, fromFPS: int, ToFPS: int) -> Tensor:
    if fromFPS < ToFPS:
        raise ValueError("Target framerate needs to be lower than source")
    # index → ToFPS → round(.) → fromFPS → round(.)
    target_fps = (index / fromFPS * ToFPS).round()
    index = (target_fps / ToFPS * fromFPS).round()
    index = index.to(torch.int32)
    return index.unique(sorted=True)


def CDAM(clip_emb: Tensor) -> Tensor:
    return clip_emb.diff(dim=1).abs().mean(dim=1)


def change_rate(CDAM: Tensor, min: float, max: float) -> Tensor:
    # clamp(min, max) → ShiftToZero → ScaleToOne
    return (CDAM.clamp(min, max) - min) / (max - min)


def normalize(CDAM: Tensor):
    min = CDAM.min()
    max = CDAM.max()
    return (CDAM - min) / (max - min)


def AAD(input: Tensor) -> Tensor:
    return (input - input.mean()).abs()


def extract_frames_index(ChangeRate: Tensor) -> Tensor:
    return ChangeRate.cumsum(0).round().diff().nonzero().flatten()
