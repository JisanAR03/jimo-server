import boto3
from botocore.client import Config
from typing import Optional, IO, Tuple
import uuid

from app.core import config
from app.utils import get_logger

log = get_logger(__name__)

class CloudflareR2Storage:
    def __init__(self):
        self.endpoint_url = config.R2_ENDPOINT_URL
        self.public_endpoint = config.R2_PUBLIC_ENDPOINT
        self.access_key_id = config.R2_ACCESS_KEY_ID
        self.secret_access_key = config.R2_SECRET_ACCESS_KEY
        self.bucket_name = config.R2_BUCKET_NAME

        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(signature_version='s3v4'),
        )

    async def upload_image(self, user_uid: str, image_id: uuid.UUID, file_obj: IO) -> Optional[Tuple[str, str]]:
        key = f"images/{user_uid}/{image_id}.jpg"
        try:
            self.s3_client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket_name,
                Key=key,
                ExtraArgs={'ContentType': 'image/jpeg'}
            )
            public_url = f"{self.public_endpoint}/{key}"
            return key, public_url
        except Exception:
            log.exception("Failed to upload image")
            return None

    async def delete_image(self, key: str):
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
        except Exception:
            log.exception("Failed to delete image")

    async def delete_user_images(self, user_uid: str):
        prefix = f"images/{user_uid}/"
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
            delete_us = []
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        delete_us.append({'Key': obj['Key']})
            if delete_us:
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': delete_us}
                )
        except Exception:
            log.exception("Failed to delete user images")
