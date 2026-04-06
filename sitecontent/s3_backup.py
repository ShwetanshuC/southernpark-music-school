import os
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

S3_KEY = "backups/db.sqlite3"


_S3_CLIENT = None

def _client():
    global _S3_CLIENT
    if _S3_CLIENT is None:
        _S3_CLIENT = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("S3_SECRET_KEY"),
        )
    return _S3_CLIENT


def _bucket():
    return os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")


def _db_path():
    return str(settings.DATABASES["default"]["NAME"])


import threading

import time

def _run_backup():
    # Small debounce to avoid overlapping uploads during rapid or bulk edits
    time.sleep(5)
    
    bucket = _bucket()
    if not bucket:
        return
    try:
        _client().upload_file(_db_path(), bucket, S3_KEY)
        print(f"[s3_backup] Database backed up to S3 successfully.")
    except Exception as e:
        print(f"[s3_backup] Upload failed: {e}")

def backup_db():
    """Upload the local SQLite DB to S3 asynchronously with a debounce delay."""
    # We use a simple daemon thread. For serious debouncing, a singleton worker thread would be better,
    # but this prevents blocking the Django request/response cycle.
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
