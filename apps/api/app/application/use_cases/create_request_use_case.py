import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Optional
from fastapi import UploadFile

from app.domain.entities.request import Request, RequestImage
from app.domain.repositories.request_repository import RequestRepository
from app.domain.services.image_storage import ImageStorage
from app.domain.services.task_queue import TaskQueue

@dataclass
class CreateRequestInput:
    client_id: uuid.UUID
    category_id: uuid.UUID
    title: str
    description: Optional[str]
    latitude: float
    longitude: float
    urgency: str
    budget_cents: Optional[int]
    images: List[UploadFile]

class CreateRequestUseCase:
    def __init__(
        self,
        request_repo: RequestRepository,
        image_storage: ImageStorage,
        task_queue: TaskQueue
    ):
        self.request_repo = request_repo
        self.image_storage = image_storage
        self.task_queue = task_queue

    async def execute(self, input_data: CreateRequestInput) -> Request:
        # 1. Preparar campos iniciais
        request_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        
        # 2. Processar Imagens e preparar os URLs
        domain_images = []
        for img in input_data.images:
            # O image_storage lida com a persistência física (disco/S3)
            image_url = await self.image_storage.save_image(img)
            
            # Aqui poderíamos ler o tamanho se necessário, ou deixar o storage retornar
            # Para manter paridade com o original:
            domain_images.append(RequestImage(
                id=uuid.uuid4(),
                request_id=request_id,
                url=image_url,
                content_type=img.content_type,
                size_bytes=0, # Opcional: o storage poderia prover isso
                created_at=now
            ))

        # 3. Criar a entidade Request
        request = Request(
            id=request_id,
            client_id=input_data.client_id,
            category_id=input_data.category_id,
            title=input_data.title,
            description=input_data.description,
            latitude=input_data.latitude,
            longitude=input_data.longitude,
            urgency=input_data.urgency,
            budget_cents=input_data.budget_cents,
            status="open",
            created_at=now,
            updated_at=now,
            images=domain_images
        )

        # 4. Persistir a entidade principal (e imagens se o repo suportar cascade)
        saved_request = await self.request_repo.save(request)

        # 5. Enfileirar Job de Análise IA (TaskQueue decoupling)
        await self.task_queue.enqueue("analyze_request_task", str(saved_request.id))

        return saved_request
