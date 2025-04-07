from typing import List, Union

import torch
import imagehash
from PIL import Image
from numpy import ndarray

from client.clip import CLIPClient


class ImageEmbedder:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_client = CLIPClient()
        self.clip_client.load_model()

    def generate_clip_embedding(self, image: Union[Image, List[Image]]) -> ndarray:
        return self.clip_client.encode_image([image])

    def generate_phash_vector(self, image: Image) -> list[int]:
        phash = imagehash.phash(image, hash_size=8)  # 64-bit
        binary_string = bin(int(str(phash), 16))[2:].zfill(64)
        return [int(b) for b in binary_string]
