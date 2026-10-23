from pathlib import Path
from urllib.request import urlretrieve

import cv2
import numpy as np
from PIL import Image

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

FILES = {
    "prototxt": (
        "colorization_deploy_v2.prototxt",
        "https://raw.githubusercontent.com/richzhang/colorization/caffe/models/colorization_deploy_v2.prototxt",
    ),
    "weights": (
        "colorization_release_v2.caffemodel",
        "https://huggingface.co/prajjwal1/bert-tiny/resolve/main/colorization_release_v2.caffemodel" 
        # Alternative direct mirror:
        # "https://eecs.berkeley.edu/~rich.zhang/projects/colorization/data/colorization_release_v2.caffemodel"
    ),
    "points": (
        "pts_in_hull.npy",
        "https://raw.githubusercontent.com/richzhang/colorization/caffe/resources/pts_in_hull.npy",
    ),
}

def get_model_files():
    paths = {}

    for name, (filename, url) in FILES.items():
        path = MODEL_DIR / filename

        if not path.exists():
            try:
                urlretrieve(url, path)
            except Exception as exc:
                if path.exists():
                    path.unlink()
                raise RuntimeError(
                    f"Could not download model file {filename}. "
                    "Check your internet connection and try again."
                ) from exc

        paths[name] = path

    return paths


def load_model():
    paths = get_model_files()

    net = cv2.dnn.readNetFromCaffe(
        str(paths["prototxt"]),
        str(paths["weights"]),
    )

    cluster_centers = np.load(paths["points"])
    cluster_centers = cluster_centers.transpose().reshape(2, 313, 1, 1)

    net.getLayer(net.getLayerId("class8_ab")).blobs = [
        cluster_centers.astype(np.float32)
    ]

    net.getLayer(net.getLayerId("conv8_313_rh")).blobs = [
        np.full((1, 313), 2.606, dtype=np.float32)
    ]

    return net


def colorize_image(image: Image.Image) -> Image.Image:
    """Return an AI-colorized RGB PIL image."""
    net = load_model()

    rgb = np.asarray(image.convert("RGB"))
    height, width = rgb.shape[:2]

    scaled = rgb.astype(np.float32) / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_RGB2LAB)

    l_channel = lab[:, :, 0]
    l_resized = cv2.resize(l_channel, (224, 224))
    l_resized -= 50

    net.setInput(cv2.dnn.blobFromImage(l_resized))
    ab = net.forward("class8_ab")[0].transpose(1, 2, 0)
    ab = cv2.resize(ab, (width, height))

    lab_out = np.concatenate(
        [l_channel[:, :, None], ab],
        axis=2,
    )

    rgb_out = cv2.cvtColor(lab_out, cv2.COLOR_LAB2RGB)
    rgb_out = np.clip(rgb_out, 0, 1)
    rgb_out = (rgb_out * 255).astype(np.uint8)

    return Image.fromarray(rgb_out, mode="RGB")
