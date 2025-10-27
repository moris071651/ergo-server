from app.utils.storage.base import StorageAdapter
from app.utils.storage.factory import create_storage_adapter


_adapter: StorageAdapter | None = None


def get_storage_adapter() -> StorageAdapter:
    global _adapter
    if _adapter is None:
        _adapter = create_storage_adapter()
        
    return _adapter
