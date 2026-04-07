import os
import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings

logger = logging.getLogger(__name__)

S3_KEY = "backups/db.sqlite3"

_S3_CLIENT = None

def _client():
    global _S3_CLIENT
    if _S3_CLIENT is None:
        access_key = os.environ.get("S3_ACCESS_KEY")
        secret_key = os.environ.get("S3_SECRET_KEY")
        if not access_key or not secret_key:
            return None
        try:
            _S3_CLIENT = boto3.client(
                "s3",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )
        except Exception as e:
            logger.error(f"[s3_backup] Failed to initialize S3 client: {e}")
            return None
    return _S3_CLIENT


def _bucket():
    return os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")


def _db_path():
    return str(settings.DATABASES["default"]["NAME"])


import shutil

def backup_db():
    """Upload the local SQLite DB to S3 synchronously.

    Called via connection.on_commit() after every admin save.
    Synchronous to ensure the backup completes before the request returns —
    daemon threads are killed on container shutdown and lose in-flight backups.
    """
    bucket = _bucket()
    client = _client()
    if not bucket or not client:
        return
    try:
        client.upload_file(_db_path(), bucket, S3_KEY)
        logger.info("[s3_backup] Database backed up to S3 successfully.")
    except Exception as e:
        logger.error(f"[s3_backup] Upload failed: {e}")


def restore_db():
    """Download the SQLite DB from S3. Returns True if restored, False otherwise."""
    bucket = _bucket()
    client = _client()
    if not bucket or not client:
        return False
        
    db_path = _db_path()
    temp_path = db_path + ".tmp"
    
    try:
        # Atomic restore: download to temp file first
        client.download_file(bucket, S3_KEY, temp_path)
        
        # Verify file size (ensure it's not empty)
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            shutil.move(temp_path, db_path)
            logger.info(f"[s3_backup] Database restored from S3 successfully.")
            return True
        else:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False
            
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.warning(f"[s3_backup] No backup found in S3 bucket.")
        else:
            logger.error(f"[s3_backup] Download failed: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False
    except Exception as e:
        logger.error(f"[s3_backup] Unexpected error during restore: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False
