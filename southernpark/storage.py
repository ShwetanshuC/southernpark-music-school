"""
Storage backends for Southern Park.

Images are stored at original quality — CloudFront caches them at the edge
so they load as fast as static files after the first request.
The only transform applied is stripping EXIF rotation metadata and baking
it into the pixel data so browsers show photos with correct orientation.
"""
from __future__ import annotations
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage


def _fix_orientation(content):
    """
    Bake EXIF rotation into pixels and return the file unchanged otherwise.
    Preserves original format and uses quality='keep' for JPEG so no
    recompression occurs. Returns (new_content, changed).
    """
    try:
        from PIL import Image, ImageOps
        content.seek(0)
        img = Image.open(content)
        original_format = img.format or "JPEG"

        img = ImageOps.exif_transpose(img)

        out = BytesIO()
        if original_format == "JPEG":
            img.save(out, format="JPEG", quality="keep", subsampling="keep")
        else:
            img.save(out, format=original_format)
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
        new_content, _ = _fix_orientation(content)
        return super()._save(name, new_content)


def _make_resizing_s3():
    from storages.backends.s3boto3 import S3Boto3Storage

    class ResizingS3Storage(S3Boto3Storage):
        def _save(self, name: str, content):
            new_content, _ = _fix_orientation(content)
            return super()._save(name, new_content)

    return ResizingS3Storage


try:
    ResizingS3Storage = _make_resizing_s3()
except Exception:
    ResizingS3Storage = None  # type: ignore
