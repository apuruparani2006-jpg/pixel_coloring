import os
import gc
import cv2
import numpy as np
import requests
import streamlit as st

MODELS_DIR = "models"
FILES = {
    "prototxt": (
        "colorization_deploy_v2.prototxt",
        "https://raw.githubusercontent.com/richzhang/colorization/caffe/models/colorization_deploy_v2.prototxt",
    ),
    "weights": (
        "colorization_release_v2.caffemodel",
        "https://storage.openvinotoolkit.org/repositories/datumaro/models/colorization/colorization_release_v2.caffemodel",
    ),
    "points": (
        "pts_in_hull.npy",
        "https://raw.githubusercontent.com/richzhang/colorization/caffe/resources/pts_in_hull.npy",
    ),
}

def download_file(filename, url):
    """Downloads Caffe model weights in 8KB chunks to avoid RAM spikes on Render free tier."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    filepath = os.path.join(MODELS_DIR, filename)
    
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return filepath
        
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()
    
    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                
    return filepath

def colorize_image(image_bytes):
    try:
        # Step 1: Ensure Caffe model files are present / downloaded dynamically
        prototxt_path = download_file(*FILES["prototxt"])
        weights_path = download_file(*FILES["weights"])
        pts_path = download_file(*FILES["points"])

        # Step 2: Load Caffe Model into OpenCV DNN
        net = cv2.dnn.readNetFromCaffe(prototxt_path, weights_path)
        pts = np.load(pts_path)

        class8 = net.getLayerId("class8_ab")
        conv8 = net.getLayerId("conv8_313_rh")
        pts = pts.transpose().reshape(2, 313, 1, 1)
        net.getLayer(class8).blobs = [pts.astype(np.float32)]
        net.getLayer(conv8).blobs = [np.full((1, 313), 2.606, dtype="float32")]

        # Step 3: Decode raw byte input into OpenCV matrix
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # Free byte array immediately to reduce memory footprint
        del np_arr
        gc.collect()

        if img is None:
            st.error("Error: Could not decode uploaded image file into image matrix.")
            return None

        # Step 4: Downscale large images (max 500px) to prevent 512MB RAM overflow
        height, width = img.shape[:2]
        max_dim = 500
        if max(height, width) > max_dim:
            scale = max_dim / float(max(height, width))
            img = cv2.resize(img, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)

        scaled = img.astype("float32") / 255.0
        lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

        resized = cv2.resize(lab, (224, 224))
        L = cv2.split(resized)[0]
        L -= 50

        net.setInput(cv2.dnn.blobFromImage(L))
        ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

        ab = cv2.resize(ab, (img.shape[1], img.shape[0]))
        L_orig = cv2.split(lab)[0]
        colorized = np.concatenate((L_orig[:, :, np.newaxis], ab), axis=2)

        colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
        colorized = np.clip(colorized * 255, 0, 255).astype("uint8")

        # Step 5: Clean up model objects from memory
        del net, pts, lab, resized, L, ab
        gc.collect()

        return colorized

    except Exception as e:
        # Display explicit technical error in Streamlit interface for quick debugging
        st.error(f"Detailed Processing Error: {str(e)}")
        return None

