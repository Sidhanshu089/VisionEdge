from pathlib import Path

import cv2
import numpy as np

IMAGE_PATH = Path("assets/images/input/test.png")


def preprocess():

    image = cv2.imread(str(IMAGE_PATH))

    if image is None:
        raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = cv2.resize(image, (640, 640))

    image = image.astype(np.float32) / 255.0

    image = np.transpose(image, (2, 0, 1))

    image = np.expand_dims(image, axis=0)

    print("Image Tensor Shape:", image.shape)
    print("Data Type:", image.dtype)

    return image


if __name__ == "__main__":
    preprocess()