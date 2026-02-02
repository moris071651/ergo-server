import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from typing import List, Union, Optional

from app.utils.storage.base import StorageAdapter


class S3Adapter(StorageAdapter):
    def __init__(
        self,
        region: str,
        access_key: str,
        secret_key: str,
        host_url: Optional[str] = None,
        endpoint_url: Optional[str] = None
    ):
        if not endpoint_url or not host_url:
            raise ValueError("S3Adapter requires both host_url and endpoint_url")

        self.s3 = boto3.client(
            "s3",
            region_name = region,
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key,
            endpoint_url = endpoint_url,
            config = Config(signature_version="s3v4"),
        )

        self.host_url = host_url 
        self.endpoint_url = endpoint_url


    def create_bucket(self, bucket: str) -> bool:
        try:
            params = {"Bucket": bucket}
            if self.endpoint_url is None or "amazonaws.com" in self.endpoint_url:
                if self.region != "us-east-1":
                    params["CreateBucketConfiguration"] = {
                        "LocationConstraint": self.region
                    }

            self.s3.create_bucket(**params)
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "BucketAlreadyOwnedByYou":
                return False
            
            elif error_code == "BucketAlreadyExists":
                raise ValueError(f"Bucket name '{bucket}' is already taken globally.")
            
            else:
                raise e


    def put_object(self, bucket: str, key: str, data: Union[bytes, str], content_type: Optional[str] = None) -> None:
        if isinstance(data, str):
            data = data.encode()

        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
            
        self.s3.put_object(Bucket=bucket, Key=key, Body=data, **extra_args)


    def get_object(self, bucket: str, key: str) -> bytes:
        res = self.s3.get_object(Bucket=bucket, Key=key)
        return res["Body"].read()


    def list_objects(self, bucket: str, prefix: str = "") -> List[str]:
        res = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return [item["Key"] for item in res.get("Contents", [])]


    def delete_object(self, bucket: str, key: str) -> None:
        self.s3.delete_object(Bucket=bucket, Key=key)


    def create_presigned_url(self, bucket: str, key: str, expires_seconds: int = 3600) -> Optional[str]:
        try:
            return self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_seconds,
            ).replace(self.endpoint_url, f"{self.host_url}/images")
        except:
            return None
