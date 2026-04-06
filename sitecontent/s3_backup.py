import os
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

S3_KEY = "backups/db.sqlite3"


def _client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("S3_SECRET_KEY"),
    )


def _bucket():
    return os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")


def _db_path():
    return str(settings.DATABASES["default"]["NAME"])


import threading

def _run_backup():
    bucket = _bucket()
    if not bucket:
        return
    try:
        _client().upload_file(_db_path(), bucket, S3_KEY)
    except Exception as e:
        print(f"[s3_backup] Upload failed: {e}")

def backup_db():
    """Upload the local SQLite DB to S3 asynchronously. No-ops if S3 is not configured."""
    thread = threading.Thread(target=_run_backup)
    thread.daemon = True
    thread.start()


def restore_db():
    """Download the SQLite DB from S3. Returns True if restored, False otherwise."""
    bucket = _bucket()
    if not bucket:
        return False
    try:
        _client().download_file(bucket, S3_KEY, _db_path())
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        print(f"[s3_backup] Download failed: {e}")
        return False
