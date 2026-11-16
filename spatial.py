"""Local monocular depth and image masks refined from detection boxes."""
import cv2
import numpy as np
from PIL import Image

from paths import DATA_DIR

DEPTH_MODEL = "depth-anything/Depth-Anything-V2-Small-hf"
MASK_COLORS = (
    (104, 209, 255), (255, 134, 106), (113, 231, 166), (221, 150, 252),
    (251, 206, 109), (111, 168, 255), (245, 137, 190), (174, 226, 102),
    (248, 111, 95), (44, 223, 219), (191, 147, 97), (171, 167, 255),
    (240, 221, 158), (118, 181, 129), (231, 149, 80), (200, 212, 237),
)


class DepthEstimator:
    def __init__(self):
        self.model = None

    def predict(self, image):
        import torch
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation

        if self.model is None:
            cache = DATA_DIR / "models"
            local_model = cache / "depth-anything-v2-small"
            source = str(local_model) if (local_model / "config.json").is_file() else DEPTH_MODEL
            self.processor = AutoImageProcessor.from_pretrained(source, cache_dir=cache, use_fast=False)
            torch.set_num_threads(min(torch.get_num_threads(), 6))
            self.model = AutoModelForDepthEstimation.from_pretrained(source, cache_dir=cache).eval()

        rgb = image.convert("RGB")
        rgb.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
        inputs = self.processor(images=rgb, return_tensors="pt")
        with torch.inference_mode():
            raw = self.model(pixel_values=inputs.pixel_values).predicted_depth
        raw = cv2.resize(raw[0].float().cpu().numpy(), rgb.size, interpolation=cv2.INTER_CUBIC)
        if not np.isfinite(raw).all():
            raise ValueError("Depth model returned non-finite values.")
        low, high = np.percentile(raw, (2, 98))
        return np.clip((raw - low) / max(high - low, 1e-6), 0, 1).astype(np.float32)


def color_depth(near):
    colored = cv2.applyColorMap(np.uint8(near * 255), cv2.COLORMAP_TURBO)
    return Image.fromarray(cv2.cvtColor(colored, cv2.COLOR_BGR2RGB))


def segment_instances(image, boxes):
    """Use each grounded object box as a GrabCut prior, with a distinct color per mask."""
    small = image.convert("RGB")
    small.thumbnail((720, 720), Image.Resampling.LANCZOS)
    rgb = np.asarray(small)
    height, width = rgb.shape[:2]
    colors = rgb.copy()
    coverage = np.zeros((height, width), dtype=bool)
    legend = []
    candidates = [box for box in boxes if box.get("kind") == "bbox"]
    # Large masks first so smaller objects stay visible.
    candidates.sort(key=lambda b: (b["xyxy"][2] - b["xyxy"][0]) *
                                  (b["xyxy"][3] - b["xyxy"][1]), reverse=True)
    for box in candidates[:16]:
        x1, y1, x2, y2 = (round(value * (width if i % 2 == 0 else height) / image.size[i % 2])
                          for i, value in enumerate(box["xyxy"]))
        if x2 - x1 < 5 or y2 - y1 < 5:
            continue
        margin = max(4, min(x2 - x1, y2 - y1) // 7)
        left, top = max(0, x1 - margin), max(0, y1 - margin)
        right, bottom = min(width, x2 + margin + 1), min(height, y2 + margin + 1)
        patch = rgb[top:bottom, left:right]
        patch = cv2.copyMakeBorder(patch, 3, 3, 3, 3, cv2.BORDER_REPLICATE)
        mask = np.zeros(patch.shape[:2], dtype=np.uint8)
        rect = (x1 - left + 3, y1 - top + 3, x2 - x1 + 1, y2 - y1 + 1)
        try:
            cv2.grabCut(patch, mask, rect, None, None, 3, cv2.GC_INIT_WITH_RECT)
        except cv2.error:
            continue
        foreground = (mask[3:-3, 3:-3] & 1).astype(bool)
        if np.count_nonzero(foreground) < 12:
            continue
        color = MASK_COLORS[len(legend) % len(MASK_COLORS)]
        colors[top:bottom, left:right][foreground] = color
        coverage[top:bottom, left:right] |= foreground
        legend.append((box.get("label", ""), color))
    overlay = np.clip(rgb.astype(np.float32) * .28 + colors * .72, 0, 255).astype(np.uint8)
    overlay[~coverage] = (rgb[~coverage] * .55).astype(np.uint8)
    return Image.fromarray(overlay), legend
