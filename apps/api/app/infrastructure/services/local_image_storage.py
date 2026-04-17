import os
import uuid
import aiofiles
from fastapi import UploadFile
from app.domain.services.image_storage import ImageStorage
from app.core.config import settings

class LocalImageStorage(ImageStorage):
    def __init__(self, base_dir: str = settings.UPLOADS_DIR):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def save_image(self, image: UploadFile) -> str:
        file_ext = image.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(self.base_dir, file_name)
        
        async with aiofiles.open(file_path, "wb") as f:
            content = await image.read()
            await f.write(content)
        
        return file_path

    def delete_image(self, path: str) -> None:
        if os.path.exists(path):
            os.remove(path)
