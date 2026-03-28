import food_density_get
import numpy as np
import visionllm
import yoloe

# import depth
import depth2 as depth
from PIL import Image
import torch
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import cv2


def fit_bowl(dct, depth_map):
    """
    Fits a Gaussian decay model to the bowl/plate surface.
    Model: depth = c + a * exp(-b * (r/scale)^2)
    """
    import numpy as np
    from scipy.optimize import least_squares

    x = np.array(dct["x"], dtype=np.float32)
    y = np.array(dct["y"], dtype=np.float32)

    # Safe indexing with bounds clipping
    h, w = depth_map.shape[:2]
    x_idx = np.clip(x.astype(int), 0, w - 1)
    y_idx = np.clip(y.astype(int), 0, h - 1)
    z = depth_map[y_idx, x_idx]

    # Internal normalization factor (image diagonal)
    scale = np.sqrt(h**2 + w**2)
    # [CLIP 1] Prevent division by zero on degenerate images
    scale = max(scale, 1e-6)

    def residuals(p):
        cx, cy, amplitude, k, offset = p

        # [CLIP 2] Hard clip parameters during optimization to prevent numerical explosion
        # Optimizers can occasionally step outside bounds during line search
        k = np.clip(k, 0.001, 100.0)  # Keep decay rate in valid physics range

        # Normalize radius to ~[0, 1] range
        r_sq = ((x - cx) ** 2 + (y - cy) ** 2) / (scale**2)

        # [CLIP 3] Clip exponent to prevent underflow/overflow in exp()
        # exp(-700) ~ 9e-305 (near double limit), exp(-20) ~ 2e-9 (sufficient precision)
        # Since k >= 0.001 and max r_sq ~ 1, min exponent is -100, so -20 is conservative
        exponent = -k * r_sq
        exponent = np.clip(exponent, -20.0, 200)

        return z - (offset + amplitude * np.exp(exponent))

    # Initialize
    z_min, z_max = np.min(z), np.max(z)
    x0 = [np.mean(x), np.mean(y), z_min - z_max, 2.0, z_max]

    # Bounds
    bounds = (
        [0.0, 0.0, -np.inf, 0.001, -np.inf],
        [float(w), float(h), np.inf, 100.0, np.inf],
    )

    # Add robust fitting options to prevent breaking on bad data
    result = least_squares(
        residuals,
        x0,
        bounds=bounds,
        method="trf",
        max_nfev=10,  # Prevent infinite iteration
        ftol=1e-6,
        xtol=1e-6,
        gtol=1e-6,
        # loss="soft_l1",  # Robust loss (Huber) to handle outliers without breaking
        f_scale=1.0,
    )

    # [CLIP 4] Clip final parameters to ensure clean output within physical bounds
    cx = float(np.clip(result.x[0], 0.0, w))
    cy = float(np.clip(result.x[1], 0.0, h))
    a = float(result.x[2])
    b = float(np.clip(result.x[3], 0.001, 100.0))
    c = float(result.x[4])

    return {
        "cx": cx,
        "cy": cy,
        "a": a,  # amplitude
        "b": b,  # decay rate
        "c": c,  # offset
        "_scale": float(scale),
    }, result.fun


def fit_bowl_flat_slope(dct, depth_map):
    """
    Fits a flat-bottom bowl model with constant-slope edges.

    Model (piecewise linear):
        depth = c                           , for r <= r_flat
        depth = c + slope * (r - r_flat)    , for r > r_flat

    where r = sqrt((x - cx)^2 + (y - cy)^2) is the radial distance from center,
    c is fixed at the minimum observed depth (flat bottom), and slope > 0
    represents the constant incline of the bowl walls.
    """
    import numpy as np
    from scipy.optimize import least_squares

    x = np.array(dct["x"], dtype=np.float32)
    y = np.array(dct["y"], dtype=np.float32)

    # Safe indexing with bounds clipping
    h, w = depth_map.shape[:2]
    x_idx = np.clip(x.astype(int), 0, w - 1)
    y_idx = np.clip(y.astype(int), 0, h - 1)
    z = depth_map[y_idx, x_idx]

    # Internal normalization factor (image diagonal)
    scale = np.sqrt(h**2 + w**2)
    # [CLIP 1] Prevent division by zero on degenerate images
    scale = max(scale, 1e-6)

    # Fix flat bottom depth at minimum observed depth as per requirement
    c = float(np.min(z))

    # Estimate max reasonable slope from data range (depth span over half-diagonal)
    z_range = np.max(z) - c
    max_slope = z_range / (scale * 0.5) if z_range > 0 else 100.0

    def residuals(p):
        cx, cy, r_flat, slope = p

        # [CLIP 2] Hard clip parameters during optimization to prevent numerical explosion
        cx = np.clip(cx, 0.0, float(w))
        cy = np.clip(cy, 0.0, float(h))
        r_flat = np.clip(r_flat, 0.0, scale)  # Flat radius cannot exceed image diagonal
        # [CLIP 3] Keep slope positive and physically plausible (prevent vertical walls or negative slopes)
        slope = np.clip(slope, 0.0, max_slope * 2.0)

        # Calculate normalized radial distance for numerical stability
        dx = (x - cx) / scale
        dy = (y - cy) / scale
        r = (
            np.sqrt(dx**2 + dy**2) * scale
        )  # Back to pixel units for comparison with r_flat

        # Piecewise linear model: flat bottom + constant slope edge
        # Using maximum creates a "hard" kink at r_flat; least_squares handles this via numerical derivatives
        r_excess = np.maximum(0.0, r - r_flat)

        # [CLIP 4] Prevent overflow in case of extreme slope values during iteration
        r_excess = np.clip(r_excess, 0.0, 1e6)

        depth_pred = c + slope * r_excess

        return z - depth_pred

    # Initialize center at data centroid
    cx0 = np.mean(x)
    cy0 = np.mean(y)

    # Initialize flat radius as half the standard deviation of radial distances (rough guess)
    # or 1/4 of image diagonal, whichever is smaller
    r_dist = np.sqrt((x - cx0) ** 2 + (y - cy0) ** 2)
    r_flat0 = min(np.std(r_dist) * 0.5, scale / 4.0)
    if r_flat0 < 1.0:
        r_flat0 = scale / 4.0  # Fallback if points are all clustered

    # Initialize slope from average gradient of the data
    slope0 = max_slope * 0.5 if max_slope > 0 else 0.1

    x0 = [cx0, cy0, r_flat0, slope0]

    # Bounds: center within image, r_flat positive up to 2x diagonal (generous), slope positive
    bounds = ([0.0, 0.0, 0.0, 0.0], [float(w), float(h), scale * 2.0, max_slope * 5.0])

    # Add robust fitting options
    result = least_squares(
        residuals,
        x0,
        bounds=bounds,
        method="trf",
        max_nfev=100,  # Prevent infinite iteration
        ftol=1e-6,
        xtol=1e-6,
        gtol=1e-6,
        f_scale=1.0,
    )

    # [CLIP 5] Clip final parameters to ensure clean output within physical bounds
    cx = float(np.clip(result.x[0], 0.0, w))
    cy = float(np.clip(result.x[1], 0.0, h))
    r_flat = float(np.clip(result.x[2], 0.0, scale * 2.0))
    slope = float(np.clip(result.x[3], 0.0, max_slope * 5.0))

    return {
        "cx": cx,
        "cy": cy,
        "r_flat": r_flat,  # Radius of the flat bottom region (pixels)
        "slope": slope,  # Slope of edge (depth units per pixel)
        "c": c,  # Flat bottom depth (fixed at min observed)
        "_scale": float(scale),
    }, result.fun


def bowl_depth(x_pts, y_pts, params):
    """Vectorized depth query using Gaussian bowl model."""
    cx = params["cx"]
    cy = params["cy"]
    amplitude = params["a"]  # now amplitude
    k = params["b"]  # now decay constant
    offset = params["c"]
    scale = params.get("_scale", 1000.0)  # fallback if loading old data

    # Apply same normalization as fitting
    r_sq = ((x_pts - cx) ** 2 + (y_pts - cy) ** 2) / (scale**2)
    return offset + amplitude * np.exp(-k * r_sq)


def bowl_depth_flat_slope(x_pts, y_pts, params):
    """
    Vectorized depth query using flat-bottom constant-slope bowl model.

    Model (piecewise linear):
        depth = c                           , for r <= r_flat
        depth = c + slope * (r - r_flat)    , for r > r_flat

    where r is the Euclidean distance from the bowl center (cx, cy).
    """
    import numpy as np

    cx = params["cx"]
    cy = params["cy"]
    c = params["c"]  # Flat bottom depth (minimum depth)
    r_flat = params["r_flat"]  # Radius of flat bottom region (pixels)
    slope = params["slope"]  # Slope of edge (depth units per pixel)

    # Calculate radial distance from center in pixel units
    r = np.sqrt((x_pts - cx) ** 2 + (y_pts - cy) ** 2)

    # Piecewise linear: flat inside r_flat, constant slope outside
    r_excess = np.maximum(0.0, r - r_flat)
    return c + slope * r_excess


def work(img_path, cached_foodlist=None):
    img = np.array(pil_img := Image.open(img_path).convert("RGB"))

    print("visionllm")
    if not cached_foodlist:
        foodlist = visionllm.find_food(img_path)
    else:
        foodlist = cached_foodlist
    print("done")
    foodlist = ["plate"] + foodlist
    print(f"{foodlist}")
    print("segmenting")
    res = yoloe.segment(img, foodlist)
    print("done")

    res_df = res.to_df()
    plate_bounds = res_df.filter(res_df["name"] == "plate")["segments"][0]
    h, w = img.shape[:2]
    plate_mask = np.zeros((h, w), dtype=np.uint8)
    plate_pts = np.array(
        [[int(x), int(y)] for x, y in zip(plate_bounds["x"], plate_bounds["y"])]
    )
    cv2.fillPoly(plate_mask, [plate_pts], 1)  # pyright: ignore
    y_coords, x_coords = np.where(plate_mask > 0)
    plate_interior = {
        "x": x_coords.astype(np.float32),
        "y": y_coords.astype(np.float32),
    }

    depthdiapx = max(plate_interior["x"]) - min(plate_interior["x"])
    platediamm = 180
    depthstuff = depth.getdepth(
        pil_img,
        plate_diameter_mm=platediamm,
        plate_diameter_px=depthdiapx,
        img_path=img_path,
    )
    depth_arr = np.array(depthstuff["depth"])
    print(f"Estimated height: {depthstuff['camera_height_mm']}")

    print("fitting")

    params, residuals = fit_bowl(plate_interior, depth_arr)

    print("tallying food masks")
    tally = np.zeros((img.shape[0], img.shape[1], len(foodlist)), dtype=np.float32)
    tally_conf = np.zeros((img.shape[0], img.shape[1], len(foodlist)), dtype=np.float32)
    for row in range(len(res_df)):
        index = res_df[row, "class"]
        if index == 0:
            continue
        seg = res_df[row, "segments"]
        xlst, ylst = seg["x"], seg["y"]
        pts = np.array([[int(x), int(y)] for x, y in zip(xlst, ylst)])
        tmp = np.zeros(tally.shape[:2], dtype=np.float32)
        tmp_conf = np.zeros(tally.shape[:2], dtype=np.float32)
        cv2.fillPoly(tmp_conf, [pts], res_df[row, "confidence"])
        cv2.fillPoly(tmp, [pts], 1)  # pyright: ignore
        tally[:, :, index] += tmp
        tally_conf[:, :, index] += tmp_conf
    tally[tally == 0] = 1
    for i in range(len(foodlist)):
        tally_conf[:, :, i] /= tally[:, :, i]
    foodmask = np.argmax(tally_conf, axis=2)

    print("calculating volumns")
    vol_dct = {t: 0 for t in foodlist}
    del vol_dct["plate"]
    A = platediamm / 1000 / (depthdiapx)
    for y in range(foodmask.shape[0]):
        for x in range(foodmask.shape[1]):
            t = foodmask[y][x]
            if t == 0:
                continue
            vol_dct[foodlist[t]] += (
                bowl_depth(x, y, params) - depth_arr[y, x]
            ) * A**2  # m^3

    m_dct = {}

    print("calculating food mass")
    for k, v in vol_dct.items():
        d = food_density_get.query(k)[0]  # g/ml
        v  # m
        m_dct[k] = abs(v * (10**6) * d / 1000)

    return m_dct


if __name__ == "__main__":
    img_path = "./data/sample3.png"
    # img_path = "./data/samplewow.jpg"
    # img_path = "./data/depthsanity/IMG_20260328_015339.jpg"
    # res = work(
    #     img_path,
    #     # cached_foodlist=[
    #     #     "plate",
    #     #     "half a hard-boiled egg",
    #     #     "a cherry tomato",
    #     #     "a piece of grilled chicken",
    #     #     "a piece of grilled chicken",
    #     #     "a piece of grilled chicken",
    #     #     "a piece of roasted pumpkin",
    #     #     "a piece of corn on the cob",
    #     #     "a broccoli floret",
    #     # ],
    # )
    img = np.array(pil_img := Image.open(img_path).convert("RGB"))
    cached_foodlist = None

    print("visionllm")
    if not cached_foodlist:
        foodlist = visionllm.find_food(img_path)
    else:
        foodlist = cached_foodlist
    print("done")
    foodlist = ["plate"] + foodlist
    print(f"{foodlist}")
    print("segmenting")
    res = yoloe.segment(img, foodlist)
    print("done")

    res_df = res.to_df()
    plate_bounds = res_df.filter(res_df["name"] == "plate")["segments"][0]
    h, w = img.shape[:2]
    plate_mask = np.zeros((h, w), dtype=np.uint8)
    plate_pts = np.array(
        [[int(x), int(y)] for x, y in zip(plate_bounds["x"], plate_bounds["y"])]
    )
    cv2.fillPoly(plate_mask, [plate_pts], 1)  # pyright: ignore
    y_coords, x_coords = np.where(plate_mask > 0)
    plate_interior = {
        "x": x_coords.astype(np.float32),
        "y": y_coords.astype(np.float32),
    }

    depthdiapx = max(plate_interior["x"]) - min(plate_interior["x"])
    platediamm = 180
    depthstuff = depth.getdepth(
        pil_img,
        plate_diameter_mm=platediamm,
        plate_diameter_px=depthdiapx,
        img_path=img_path,
    )
    depth_arr = np.array(depthstuff["depth"])
    print(f"Estimated height: {depthstuff['camera_height_mm']}")

    print("fitting")

    params, residuals = fit_bowl(plate_interior, depth_arr)

    print("tallying food masks")
    tally = np.zeros((img.shape[0], img.shape[1], len(foodlist)), dtype=np.float32)
    tally_conf = np.zeros((img.shape[0], img.shape[1], len(foodlist)), dtype=np.float32)
    for row in range(len(res_df)):
        index = res_df[row, "class"]
        if index == 0:
            continue
        seg = res_df[row, "segments"]
        xlst, ylst = seg["x"], seg["y"]
        pts = np.array([[int(x), int(y)] for x, y in zip(xlst, ylst)])
        tmp = np.zeros(tally.shape[:2], dtype=np.float32)
        tmp_conf = np.zeros(tally.shape[:2], dtype=np.float32)
        cv2.fillPoly(tmp_conf, [pts], res_df[row, "confidence"])
        cv2.fillPoly(tmp, [pts], 1)  # pyright: ignore
        tally[:, :, index] += tmp
        tally_conf[:, :, index] += tmp_conf
    tally[tally == 0] = 1
    for i in range(len(foodlist)):
        tally_conf[:, :, i] /= tally[:, :, i]
    foodmask = np.argmax(tally_conf, axis=2)

    print("calculating volumns")
    vol_dct = {t: 0 for t in foodlist}
    del vol_dct["plate"]
    A = platediamm / 1000 / (depthdiapx)
    for y in range(foodmask.shape[0]):
        for x in range(foodmask.shape[1]):
            t = foodmask[y][x]
            if t == 0:
                continue
            vol_dct[foodlist[t]] += (
                bowl_depth(x, y, params) - depth_arr[y, x]
            ) * A**2  # m^3

    m_dct = {}

    print("calculating food mass")
    for k, v in vol_dct.items():
        d = food_density_get.query(k)[0]  # g/ml
        v  # m
        m_dct[k] = abs(v * (10**6) * d / 1000)
    print(m_dct)
