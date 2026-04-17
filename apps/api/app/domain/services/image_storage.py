from abc import ABC, abstractmethod
from typing import List
from fastapi import UploadFile

class ImageStorage(ABC):
    @abstractmethod
    async def save_image(self, image: UploadFile) -> str:
        """Saves an image and returns its URL/Path."""
        pass

    @abstractmethod
    def delete_image(self, path: str) -> None:
        """Deletes an image by its path."""
        pass
