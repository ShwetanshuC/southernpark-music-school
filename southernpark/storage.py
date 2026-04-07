"""
Storage backends that resize images on upload.

Max dimension: 1920px on longest side — sufficient for any display including Retina.
Quality: 88 — visually lossless, roughly 60-80% smaller than a raw camera JPEG.
"""
from __future__ import annotations
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

MAX_DIM = 1920
JPEG_QUALITY = 88


def _resize(content, max_dim: int = MAX_DIM):
    """
    Return (new_content, needs_rename_to_jpg).
    Returns the original unchanged if already small or not a raster image.
    """
    try:
        from PIL import Image
        content.seek(0)
        img = Image.open(content)

        if max(img.size) <= max_dim:
            content.seek(0)
            return content, False

        ratio = max_dim / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))

        # Flatten alpha before saving as JPEG
        if img.mode in ("RGBA", "P", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            mask = img.split()[-1] if img.mode in ("RGBA", "LA") else None
            bg.paste(img, mask=mask)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        img = img.resize(new_size, Image.LANCZOS)
        out = BytesIO()
        img.save(out, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        out.seek(0)
        return ContentFile(out.read()), True
    except Exception:
        try:
            content.seek(0)
        except Exception:
            pass
        return content, False


class ResizingFileSystemStorage(FileSystemStorage):
    def _save(self, name: str, content):
        new_content, rename = _resize(content)
        if rename and "." in name:
            name = name.rsplit(".", 1)[0] + ".jpg"
        return super()._save(name, new_content)


# S3 backend is imported lazily to avoid errors when storages isn't installed
def _make_resizing_s3():
    from storages.backends.s3boto3 import S3Boto3Storage

    class ResizingS3Storage(S3Boto3Storage):
        def _save(self, name: str, content):
            new_content, rename = _resize(content)
            if rename and "." in name:
                name = name.rsplit(".", 1)[0] + ".jpg"
            return super()._save(name, new_content)

    return ResizingS3Storage


# Eagerly create for import convenience in settings.py
try:
    ResizingS3Storage = _make_resizing_s3()
except Exception:
    ResizingS3Storage = None  # type: ignore
