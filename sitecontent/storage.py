"""
Custom storage backend that auto-resizes images before upload.
Keeps the original file format where possible, falling back to JPEG.
Max dimension: 1920px on the long edge. JPEG quality: 85.
"""
from __future__ import annotations

import io
import os

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

try:
    from storages.backends.s3boto3 import S3Boto3Storage as _S3Base
    _HAS_S3 = True
except ImportError:
    _HAS_S3 = False

from PIL import Image

MAX_LONG_EDGE = 1920
JPEG_QUALITY = 85
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".bmp", ".tiff"}


def _resize_image_file(file_obj, filename: str):
    """
    Open the uploaded file, resize if necessary, re-compress, and return a
    ContentFile with the processed bytes. Returns (content_file, new_filename).
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in IMAGE_EXTENSIONS:
        return None, filename  # not an image — skip

    try:
        file_obj.seek(0)
        img = Image.open(file_obj)
        img.load()

        # Resize if either dimension exceeds MAX_LONG_EDGE
        w, h = img.size
        if max(w, h) > MAX_LONG_EDGE:
            ratio = MAX_LONG_EDGE / max(w, h)
            new_size = (int(w * ratio), int(h * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # Convert palette/RGBA to RGB for JPEG output (JPEG doesn't support transparency)
        output_format = "JPEG"
        new_ext = ".jpg"
        if ext in {".png", ".webp"} and img.mode in ("RGBA", "LA", "P"):
            # Keep PNG for transparent images; convert palette to RGBA first
            if img.mode == "P":
                img = img.convert("RGBA")
            output_format = "PNG"
            new_ext = ".png"
        elif img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        buf = io.BytesIO()
        save_kwargs = {"format": output_format, "optimize": True}
        if output_format == "JPEG":
            save_kwargs["quality"] = JPEG_QUALITY
        img.save(buf, **save_kwargs)
        buf.seek(0)

        new_filename = os.path.splitext(filename)[0] + new_ext
        return ContentFile(buf.read()), new_filename

    except Exception:
        # If anything fails, fall back to the original file unchanged
        file_obj.seek(0)
        return None, filename


class ResizingFileSystemStorage(FileSystemStorage):
    def _save(self, name, content):
        processed, name = _resize_image_file(content, name)
        if processed is not None:
            content = processed
        return super()._save(name, content)


if _HAS_S3:
    class ResizingS3Storage(_S3Base):
        def _save(self, name, content):
            processed, name = _resize_image_file(content, name)
            if processed is not None:
                content = processed
            return super()._save(name, content)
