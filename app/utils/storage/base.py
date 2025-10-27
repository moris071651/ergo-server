from abc import ABC, abstractmethod
from typing import List, Optional, Union


class StorageAdapter(ABC):

    @abstractmethod
    def put_object(self, bucket: str, key: str, data: Union[bytes, str], content_type: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def get_object(self, bucket: str, key: str) -> bytes:
        pass

    @abstractmethod
    def list_objects(self, bucket: str, prefix: str = "") -> List[str]:
        pass

    @abstractmethod
    def delete_object(self, bucket: str, key: str) -> None:
        pass

    @abstractmethod
    def create_presigned_url(self, bucket: str, key: str, expires_seconds: int = 3600) -> str:
        pass
    