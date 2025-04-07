import os
from typing import List

import numpy as np
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel


class CLIPClient:
    def __init__(
            self,
            model_name='openai/clip-vit-base-patch32',
            model_dir='./data/models'
    ):
        """
        Initialize the CLIP client with a specified model.

        Args:
            model_name (str): The name of the CLIP model to use. Default is 'ViT-B/32'.
        """
        self.model = None
        self.processor = None
        self._model_name = model_name
        self._model_dir = model_dir

        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
        self._device = device

    def load_model(self):
        """
        Load the CLIP model and processor. If the model is already downloaded, load it from the local directory.
        :return:
        """
        print("Loading CLIP model...")
        # Load the CLIP processor and model
        clip_model_path = os.path.join(self._model_dir, self._model_name)
        if os.path.exists(clip_model_path):
            # load the model weights locally
            self.processor = CLIPProcessor.from_pretrained(clip_model_path)
            self.model = CLIPModel.from_pretrained(clip_model_path)
            src = "LOCAL"
        else:
            self.processor = CLIPProcessor.from_pretrained(self._model_name)
            self.model = CLIPModel.from_pretrained(self._model_name)
            # Save the model weights
            self.model.save_pretrained(clip_model_path)
            self.processor.save_pretrained(clip_model_path)
            src = "HUGGINGFACE"

        print(f"CLIP model loaded successfully from {src}.")

        self.model.to(self._device)
        self.model.eval()
        print("CLIP model set to EVAL Mode.")

    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text using the CLIP model.

        Args:
            text (str): The text to encode.

        Returns:
            np.ndarray: The encoded text representation.
        """
        inputs = self.processor(text=text, return_tensors="pt", padding=True)
        outputs = self.model.get_text_features(**inputs)
        # Normalize the image features
        outputs = outputs / outputs.norm(dim=-1, keepdim=True)
        # Move the outputs to the appropriate device
        outputs = outputs.to(self._device).squeeze().detach().numpy()
        return outputs  # Convert to numpy array for consistency with other methods

    def encode_image(self, image: List[Image]) -> np.ndarray:
        """
        Encode an image using the CLIP model.

        Args:
            image (PIL.Image): The image to encode.

        Returns:
            np.ndarray: The encoded image representation.
        """
        inputs = self.processor(images=image, return_tensors="pt").to(self._device)
        outputs = self.model.get_image_features(**inputs)
        # Normalize the image features
        outputs = outputs / outputs.norm(dim=-1, keepdim=True)
        # Move the outputs to the appropriate device
        outputs = outputs.to('cpu').squeeze().detach().numpy()
        return outputs  # Convert to numpy array for consistency with other methods
