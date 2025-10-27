import os
from app.config.settings import STORAGE_AWS_ACCESS_KEY_ID, STORAGE_AWS_REGION, STORAGE_AWS_SECRET_ACCESS_KEY, STORAGE_ENDPOINT, STORAGE_PROVIDER

from app.utils.storage.base import StorageAdapter
from app.utils.storage.s3_adapter import S3Adapter


def create_storage_adapter() -> StorageAdapter:
    provider = STORAGE_PROVIDER

    if provider in ("s3", "minio"):
        region = STORAGE_AWS_REGION
        access_key = STORAGE_AWS_ACCESS_KEY_ID
        secret_key = STORAGE_AWS_SECRET_ACCESS_KEY
        endpoint = STORAGE_ENDPOINT

        return S3Adapter(region, access_key, secret_key, endpoint)

    else:
        raise ValueError(f"Unknown STORAGE_PROVIDER: {provider}")
