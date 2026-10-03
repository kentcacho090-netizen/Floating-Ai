"""
On-demand screen capture + cursor-focused crop.
Images live only in memory and are discarded after use.
"""

from io import BytesIO
from typing import Optional, Tuple

import mss
from PIL import Image

from kent.config import CURSOR_CROP_SIZE


def capture_cursor_region(mouse_x: int, mouse_y: int,
                          crop_size: int = CURSOR_CROP_SIZE) -> Optional[Image.Image]:
    """
    Capture a region centered on the current mouse position.
    Returns a PIL Image or None on failure.
    """
    try:
        with mss.mss() as sct:
            # Virtual desktop bounds
            mon = sct.monitors[0]  # all monitors combined
            left = mon["left"]
            top = mon["top"]
            width = mon["width"]
            height = mon["height"]

            half = crop_size // 2
            x1 = max(left, mouse_x - half)
            y1 = max(top, mouse_y - half)
            x2 = min(left + width, mouse_x + half)
            y2 = min(top + height, mouse_y + half)

            region = {
                "left": x1,
                "top": y1,
                "width": max(1, x2 - x1),
                "height": max(1, y2 - y1),
            }

            shot = sct.grab(region)
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

            # Keep size reasonable for the API
            max_side = 1280
            if max(img.size) > max_side:
                img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

            return img
    except Exception as e:
        print(f"[screen] capture failed: {e}")
        return None


def image_to_bytes(img: Image.Image, fmt: str = "JPEG", quality: int = 85) -> bytes:
    buf = BytesIO()
    img.save(buf, format=fmt, quality=quality)
    return buf.getvalue()
