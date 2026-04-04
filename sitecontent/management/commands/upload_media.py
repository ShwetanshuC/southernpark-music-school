import os
from pathlib import Path
import boto3
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Upload all local media files to S3"

    def handle(self, *args, **options):
        bucket = os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")
        if not bucket:
            self.stderr.write("S3_AWS_STORAGE_BUCKET_NAME not set — aborting.")
            return

        client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("S3_SECRET_KEY"),
        )

        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            self.stderr.write(f"MEDIA_ROOT {media_root} does not exist.")
            return

        uploaded = 0
        for file_path in media_root.rglob("*"):
            if file_path.is_file():
                key = str(file_path.relative_to(media_root))
                client.upload_file(str(file_path), bucket, key)
                self.stdout.write(f"  uploaded: {key}")
                uploaded += 1

        self.stdout.write(f"\nDone — {uploaded} file(s) uploaded to s3://{bucket}/")
