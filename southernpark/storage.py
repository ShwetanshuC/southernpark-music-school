"""
Storage backends for Southern Park.

Converts uploads to progressive JPEG (quality 95) — the image renders
immediately blurry then sharpens in passes, eliminating top-to-bottom
chunk loading. Also fixes EXIF rotation. Caps width at MAX_PX (2560px)
to keep file sizes web-appropriate; this covers any retina display with
no visible quality difference.
"""
from __future__ import annotations
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

# Maximum dimension (longest edge). 3840px = true 4K / MacBook Pro Liquid Retina.
MAX_PX = 3840


def _process(content):
    """
    Convert to progressive JPEG at quality 95, fix EXIF rotation, and
    downscale if either dimension exceeds MAX_PX (aspect ratio preserved).
    Returns (new_content, ext) where ext is '.jpg', or (original, None) on failure.
    """
    try:
        from PIL import Image, ImageOps
        content.seek(0)
        img = Image.open(content)
        img = ImageOps.exif_transpose(img)

        # Downscale only if needed — longest edge capped at MAX_PX
        w, h = img.size
        if max(w, h) > MAX_PX:
            if w >= h:
                img = img.resize((MAX_PX, round(h * MAX_PX / w)), Image.LANCZOS)
            else:
                img = img.resize((round(w * MAX_PX / h), MAX_PX), Image.LANCZOS)

        if img.mode in ("RGBA", "P", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            mask = img.split()[-1] if img.mode in ("RGBA", "LA") else None
            bg.paste(img, mask=mask)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        out = BytesIO()
        img.save(out, format="JPEG", quality=95, progressive=True, optimize=True)
        out.seek(0)
        return ContentFile(out.read()), ".jpg"
    except Exception:
        try:
            content.seek(0)
        except Exception:
            pass
        return content, None


class ResizingFileSystemStorage(FileSystemStorage):
    def _save(self, name: str, content):
        new_content, ext = _process(content)
        if ext and "." in name:
            name = name.rsplit(".", 1)[0] + ext
        return super()._save(name, new_content)


def _make_resizing_s3():
    from storages.backends.s3boto3 import S3Boto3Storage
    from django.conf import settings
    from pathlib import Path

    class ResizingS3Storage(S3Boto3Storage):
        def _save(self, name: str, content):
            new_content, ext = _process(content)
            if ext and "." in name:
                name = name.rsplit(".", 1)[0] + ext
            saved_name = super()._save(name, new_content)

            # Mirror to local disk so nginx serves instantly without CloudFront round-trip
            try:
                local_path = Path(settings.MEDIA_ROOT) / saved_name
                local_path.parent.mkdir(parents=True, exist_ok=True)
                new_content.seek(0)
                local_path.write_bytes(new_content.read())
            except Exception:
                pass

            return saved_name

    return ResizingS3Storage


try:
    ResizingS3Storage = _make_resizing_s3()
except Exception:
    ResizingS3Storage = None  # type: ignore
