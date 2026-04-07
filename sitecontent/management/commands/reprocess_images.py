"""
Download every media image from S3, re-encode as progressive JPEG
(quality 95, max 2560px), and re-upload to the same S3 key.

Run once after deployment to fix baseline JPEGs uploaded before the
progressive-JPEG storage backend was added:

    python manage.py reprocess_images

Pass --dry-run to list files without changing them.
Pass --force to re-encode even images that are already progressive.
"""
import os
import io
import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from southernpark.storage import _process, MAX_PX


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}


class Command(BaseCommand):
    help = "Re-encode all S3 media images to progressive JPEG (quality 95)"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="List files without re-encoding")
        parser.add_argument("--force", action="store_true", help="Re-encode even already-progressive images")

    def handle(self, *args, **options):
        bucket = os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")
        access_key = os.environ.get("S3_ACCESS_KEY")
        secret_key = os.environ.get("S3_SECRET_KEY")

        if not bucket or not access_key or not secret_key:
            self.stderr.write("[reprocess_images] ERROR: S3 credentials not set.")
            return

        client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        dry_run = options["dry_run"]
        force = options["force"]
        paginator = client.get_paginator("list_objects_v2")

        processed = 0
        skipped = 0
        errors = 0

        try:
            for page in paginator.paginate(Bucket=bucket):
                for obj in page.get("Contents", []):
                    key = obj["Key"]

                    # Skip DB backup
                    if key.startswith("backups/"):
                        continue

                    ext = os.path.splitext(key)[1].lower()
                    if ext not in IMAGE_EXTENSIONS:
                        skipped += 1
                        continue

                    if dry_run:
                        self.stdout.write(f"  [dry-run] Would process: {key} ({obj['Size'] // 1024} KB)")
                        processed += 1
                        continue

                    try:
                        # Download
                        resp = client.get_object(Bucket=bucket, Key=key)
                        original_bytes = resp["Body"].read()
                        original_size = len(original_bytes)

                        if not force:
                            # Quick check: is it already a small progressive JPEG?
                            # Progressive JPEGs have an SOF2 marker (0xFF 0xC2)
                            if _is_progressive_jpeg(original_bytes):
                                # Also check if already within size limits
                                from PIL import Image
                                img_check = Image.open(io.BytesIO(original_bytes))
                                w, h = img_check.size
                                if max(w, h) <= MAX_PX:
                                    skipped += 1
                                    continue

                        # Re-encode
                        content_file = io.BytesIO(original_bytes)
                        new_content, new_ext = _process(content_file)

                        if new_ext is None:
                            self.stderr.write(f"  [skip] Could not process: {key}")
                            errors += 1
                            continue

                        new_bytes = new_content.read()
                        new_size = len(new_bytes)

                        # Determine new key (may change extension to .jpg)
                        if new_ext and "." in key:
                            new_key = key.rsplit(".", 1)[0] + new_ext
                        else:
                            new_key = key

                        # Upload with 1-year cache
                        client.put_object(
                            Bucket=bucket,
                            Key=new_key,
                            Body=new_bytes,
                            ContentType="image/jpeg",
                            CacheControl="max-age=31536000, public",
                        )

                        # Delete old key if extension changed
                        if new_key != key:
                            client.delete_object(Bucket=bucket, Key=key)

                        delta = new_size - original_size
                        sign = "+" if delta > 0 else ""
                        self.stdout.write(
                            f"  OK  {key} → {new_key}  "
                            f"{original_size // 1024} KB → {new_size // 1024} KB  "
                            f"({sign}{delta // 1024} KB)"
                        )
                        processed += 1

                    except ClientError as e:
                        self.stderr.write(f"  ERROR {key}: {e}")
                        errors += 1
                    except Exception as e:
                        self.stderr.write(f"  ERROR {key}: {e}")
                        errors += 1

        except ClientError as e:
            self.stderr.write(f"[reprocess_images] ERROR listing S3: {e}")
            return

        action = "Would process" if dry_run else "Processed"
        self.stdout.write(
            f"\n[reprocess_images] DONE — {action} {processed}, skipped {skipped}, errors {errors}"
        )


def _is_progressive_jpeg(data: bytes) -> bool:
    """Return True if data is a progressive JPEG (contains SOF2 marker 0xFF 0xC2)."""
    return b"\xff\xc2" in data
