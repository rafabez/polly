"""
Vision/screen context for Polly (WU-17).

Lets Polly "see" an image or screenshot to reason about it.
Opt-in only — never captures anything automatically.

Entry points:
  encode_image(path) -> str          base64-encoded image for the API
  capture_screenshot() -> Path|None  capture screen to a temp file
  query_with_image(api, image_path, prompt) -> str
"""

import base64
import sys
import tempfile
from pathlib import Path
from typing import Optional

from .i18n import get_text
from .utils import print_info


# Vision-capable models on Pollinations (input_modalities includes "image")
_VISION_MODELS = {
    "openai",
    "openai-fast",
    "openai-large",
    "gpt-5.4-mini",
    "gpt-5.5",
    "mistral",
    "mistral-4",
    "gemini",
    "gemini-3.5-flash",
    "gemini-flash-lite-3.1",
    "gemini-fast",
    "gemma",
    "grok",
    "grok-large",
    "grok-4.3",
    "llama-maverick",
    "qwen-vision",
    "qwen-vision-pro",
    "step-flash",
    "kimi",
    "kimi-k2.6",
    "gemini-large",
}


def is_vision_model(model_name: str) -> bool:
    """Return True if this model accepts image input."""
    return model_name.lower() in _VISION_MODELS


def encode_image(path: str) -> tuple[str, str]:
    """
    Read an image file and return (base64_data, media_type).
    Supports PNG, JPEG, GIF, WEBP.
    """
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    suffix = p.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_types.get(suffix, "image/png")

    data = base64.standard_b64encode(p.read_bytes()).decode("utf-8")
    return data, media_type


def capture_screenshot() -> Optional[Path]:
    """
    Capture the current screen to a temp PNG file.
    Uses platform-native tools; returns None if unavailable.
    """
    tmp = Path(tempfile.mktemp(suffix=".png", prefix="polly_screenshot_"))

    if sys.platform == "win32":
        # PowerShell: Add-Type + BitBlt screenshot
        import subprocess
        ps_cmd = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "$screen = [System.Windows.Forms.Screen]::PrimaryScreen;"
            "$bmp = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height);"
            "$g = [System.Drawing.Graphics]::FromImage($bmp);"
            "$g.CopyFromScreen($screen.Bounds.Location, [System.Drawing.Point]::Empty, $screen.Bounds.Size);"
            f"$bmp.Save('{tmp}', [System.Drawing.Imaging.ImageFormat]::Png);"
            "$g.Dispose(); $bmp.Dispose()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            timeout=15,
        )
        return tmp if tmp.exists() else None

    elif sys.platform == "darwin":
        import subprocess
        subprocess.run(
            ["screencapture", "-x", str(tmp)],
            capture_output=True,
            timeout=15,
        )
        return tmp if tmp.exists() else None

    else:
        # Linux: try scrot, then gnome-screenshot, then import (ImageMagick)
        import subprocess
        for cmd in [
            ["scrot", str(tmp)],
            ["gnome-screenshot", "-f", str(tmp)],
            ["import", "-window", "root", str(tmp)],
        ]:
            try:
                subprocess.run(cmd, capture_output=True, timeout=10)
                if tmp.exists():
                    return tmp
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return None


def query_with_image(api, image_path: str, prompt: str) -> str:
    """
    Send an image + prompt to a vision-capable model.
    Automatically picks a vision model if the configured default doesn't support images.
    Returns the model's response.
    """
    from .config import get_config
    config = get_config()

    model = config.get("default_model", "openai")
    if not is_vision_model(model):
        # Pick the first available vision model
        model = "openai"
        print_info(get_text("vision.model_switch", model=model))

    try:
        data, media_type = encode_image(image_path)
    except FileNotFoundError as e:
        raise Exception(get_text("vision.not_found", path=image_path)) from e

    # OpenAI vision message format
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{media_type};base64,{data}"},
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]

    return api.chat_completion(messages=messages, model=model)
