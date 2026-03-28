import os
from PIL.ExifTags import TAGS
import sys
from PIL import Image, ExifTags
import numpy as np
import torch

import io
from PIL import Image
import exifread


def get_focal_length_px(image_input):
    """
    Extract focal length from EXIF and convert to pixels.
    Handles: file paths (str), PIL Images, numpy arrays
    """
    # Normalize input to get both a PIL Image and a file-like object
    if isinstance(image_input, str):
        # File path: read EXIF directly from file
        img = Image.open(image_input)
        f = open(image_input, "rb")
        should_close = True
    elif isinstance(image_input, Image.Image):
        img = image_input
        # If PIL image has filename attached, read from disk (preserves original EXIF)
        if hasattr(image_input, "filename") and image_input.filename:
            try:
                f = open(image_input.filename, "rb")
                should_close = True
            except (FileNotFoundError, IOError):
                # Fallback: dump to buffer (may lose EXIF if not preserved in memory)
                f = io.BytesIO()
                fmt = image_input.format if image_input.format else "JPEG"
                image_input.save(f, format=fmt)
                f.seek(0)
                should_close = False
        else:
            # In-memory image: serialize to buffer for exifread
            f = io.BytesIO()
            fmt = image_input.format if image_input.format else "JPEG"
            image_input.save(f, format=fmt)
            f.seek(0)
            should_close = False
    else:
        # Numpy array: convert to PIL first
        img = Image.fromarray(image_input)
        f = io.BytesIO()
        img.save(f, format="JPEG")
        f.seek(0)
        should_close = False

    try:
        # Use exifread for comprehensive EXIF parsing (includes MakerNotes, GPS, etc.)
        tags = exifread.process_file(f, details=False)

        if not tags:
            print("No EXIF data found")
            return None

        width = img.size[0]
        focal_mm = None
        focal_35mm = None

        # Helper: extract float from rational (e.g., "49/10" → 4.9)
        def rational_to_float(tag_obj):
            if tag_obj is None:
                return None
            val = tag_obj.values[0]  # exifread returns list of values
            if hasattr(val, "num") and hasattr(val, "den"):
                return float(val.num) / float(val.den)
            return float(val)

        # Extract focal length (tag 0x920A)
        if "EXIF FocalLength" in tags:
            focal_mm = rational_to_float(tags["EXIF FocalLength"])

        # Extract 35mm equivalent (tag 0x9205) - crucial for crop factor calculation
        if "EXIF FocalLengthIn35mmFilm" in tags:
            focal_35mm = rational_to_float(tags["EXIF FocalLengthIn35mmFilm"])

        if focal_mm is None:
            print("Focal length (EXIF FocalLength) not found")
            return None

        # Calculate sensor width from crop factor
        if focal_35mm and focal_mm > 0:
            crop_factor = focal_35mm / focal_mm
            sensor_width = 36.0 / crop_factor  # 36mm is full-frame width
        else:
            sensor_width = 5.76  # Fallback: common smartphone sensor (1/2.3")
            print(
                f"Warning: No 35mm equivalent found, assuming sensor width {sensor_width}mm"
            )

        # Convert focal length from mm to pixels
        focal_px = focal_mm * (width / sensor_width)
        return focal_px

    except Exception as e:
        print(f"EXIF extraction failed: {e}")
        return None
    finally:
        if should_close:
            f.close()


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Depth-Anything-V2"))
os.chdir("./Depth-Anything-V2/")
from depth_anything_v2.util.transform import Resize, NormalizeImage, PrepareForNet

os.chdir("../")

from transformers import pipeline

pipe = pipeline(
    task="depth-estimation",
    model="Depth-Anything-V2-Metric-Indoor-Base-hf",
    local_files_only=True,
)


def getdepth(
    image,
    plate_diameter_mm=None,
    plate_diameter_px=None,
    focal_length_px=None,
    sample_point=None,
    img_path=None,
):
    """
    Get metric depth normalized using plate geometry.

    Args:
        image: Input image (PIL, numpy, or path)
        plate_diameter_mm: Physical plate diameter in mm (e.g., 250.0 for 25cm)
        plate_diameter_px: Plate diameter in pixels (from your XY measurement)
        focal_length_px: Camera focal length in pixels (auto-extracted from EXIF if None)
        sample_point: (x, y) tuple to sample depth at plate surface.
                     If None, uses image center.

    Returns:
        dict: {
            'depth': Normalized depth map (numpy array, meters),
            'scale': Scale factor applied to raw depth,
            'camera_height_mm': Expected camera height from geometry
        }
    """
    # Load image
    if isinstance(image, str):
        pil_img = Image.open(image).convert("RGB")
    elif isinstance(image, np.ndarray):
        pil_img = Image.fromarray(image).convert("RGB")
    else:
        pil_img = image

    # Get raw depth
    depth_raw = pipe(pil_img)["depth"]
    if isinstance(depth_raw, Image.Image):
        depth_np = np.array(depth_raw).astype(np.float32)
    elif torch.is_tensor(depth_raw):
        depth_np = depth_raw.cpu().numpy().astype(np.float32)
    else:
        depth_np = depth_raw.astype(np.float32)

    # If no calibration data, return raw
    if plate_diameter_mm is None or plate_diameter_px is None:
        return {"depth": depth_np, "scale": 1.0, "camera_height_mm": None}

    # Get focal length in pixels
    f_px = focal_length_px if focal_length_px else get_focal_length_px(img_path)
    if f_px is None:
        # raise ValueError(
        #     "No focal length found in EXIF. Provide focal_length_px manually."
        # )
        print("No focal length found in EXIF. Fallin back to default.")
        f_px = 6

    # Calculate expected camera height: H = (f_px * D_real) / D_px
    camera_height_mm = (f_px * plate_diameter_mm) / plate_diameter_px

    # Sample depth at plate center
    h, w = depth_np.shape
    if sample_point:
        cx, cy = int(sample_point[0]), int(sample_point[1])
    else:
        cx, cy = w // 2, h // 2

    # Average small neighborhood for robustness
    size = 3
    raw_depth_at_plate = float(
        np.mean(
            depth_np[
                max(0, cy - size) : min(h, cy + size),
                max(0, cx - size) : min(w, cx + size),
            ]
        )
    )

    # Calculate scale: expected / measured
    camera_height_m = camera_height_mm / 1000.0
    scale = camera_height_m / raw_depth_at_plate

    # Apply correction
    depth_normalized = depth_np * scale

    return {
        "depth": depth_normalized,
        "scale": float(scale),
        "camera_height_mm": float(camera_height_mm),
        "raw_depth_at_plate": float(raw_depth_at_plate),
        "corrected_depth_at_plate": float(raw_depth_at_plate * scale),
    }


# Backwards compatibility
def getdepth_raw(image):
    """Original interface without calibration."""
    depth = pipe(image)["depth"]
    if isinstance(depth, Image.Image):
        return np.array(depth)
    elif torch.is_tensor(depth):
        return depth.cpu().numpy()
    return depth
