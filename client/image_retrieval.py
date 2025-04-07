import os
from typing import List, Union

import torch
from PIL import Image

from client.clip import clip_client


class ImageRetrieval:
    def __init__(
            self,
            image_dirs: Union[str, List[str], os.PathLike[str]],
            batch_size: int = 32
    ):
        assert image_dirs, "Image directories cannot be empty"
        if isinstance(image_dirs, str):
            image_dirs = [image_dirs]

        assert all(os.path.isdir(d) for d in image_dirs), "All paths must be valid directories"

        self._image_dirs = image_dirs
        self._image_paths = []
        self.batch_size = batch_size  # Number of images to process in each batch

    def ingest_images(self):
        for directory in self._image_dirs:
            print(f"Ingesting images from directory: {directory}")
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(root, file)
                        self._image_paths.append(image_path)
        self.load_image()
        self.preprocess_image()
        self.retrieve_similar_images()
        # Placeholder for image loading logic

    def preprocess_image(self):
        # Placeholder for image preprocessing logic
        print("Preprocessing image")

    def retrieve_similar_images(self):
        # Placeholder for image retrieval logic
        print("Retrieving similar images")

    def load_image(self):
        # Placeholder for image loading logic
        print("Loading images")
        # Process images in mini - batches
        for i in range(0, len(self._image_paths), self.batch_size):
            batch_paths = self._image_paths[i:i + self.batch_size]
            valid_images = []
            valid_paths = []
            for path in batch_paths:
                try:
                    img = Image.open(path).convert("RGB")
                    valid_images.append(img)
                    valid_paths.append(path)
                except Exception as e:
                    print(f"Error processing {path}: {e}")
            if len(valid_images) == 0:
                continue

            valid_image_embeddings: torch.Tensor = clip_client.encode_image(valid_images)
