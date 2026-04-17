import { apiFetch } from "@/lib/api";
import { ServiceRequest } from "../../domain/models/request";
import { RequestRepository, CreateRequestPayload } from "../../domain/repositories/request.repository";

export class RequestRepositoryImpl implements RequestRepository {
    private mapToEntity(data: any): ServiceRequest {
        return {
            id: data.id,
            clientId: data.client_id,
            categoryId: data.category_id,
            title: data.title,
            description: data.description,
            latitude: data.latitude,
            longitude: data.longitude,
            urgency: data.urgency,
            budgetCents: data.budget_cents,
            status: data.status,
            createdAt: data.created_at,
            updatedAt: data.updated_at,
            images: (data.images || []).map((img: any) => ({
                id: img.id,
                requestId: img.request_id,
                url: img.url,
                contentType: img.content_type,
                sizeBytes: img.size_bytes,
                analyzed: img.analyzed,
                createdAt: img.created_at,
            })),
        };
    }

    async listMine(limit = 10): Promise<ServiceRequest[]> {
        const data = await apiFetch(`/requests?client_only=true&limit=${limit}`);
        return data.map(this.mapToEntity);
    }

    async getById(id: string): Promise<ServiceRequest> {
        const data = await apiFetch(`/requests/${id}`);
        return this.mapToEntity(data);
    }

    async create(payload: CreateRequestPayload): Promise<ServiceRequest> {
        const formData = new FormData();
        formData.append("title", payload.title);
        if (payload.description) formData.append("description", payload.description);
        formData.append("category_id", payload.category_id);
        formData.append("urgency", payload.urgency);
        formData.append("latitude", String(payload.latitude));
        formData.append("longitude", String(payload.longitude));
        if (payload.budget_cents) formData.append("budget_cents", String(payload.budget_cents));
        payload.images?.forEach((img) => formData.append("images", img));

        const data = await apiFetch("/requests", {
            method: "POST",
            body: formData,
        });
        return this.mapToEntity(data);
    }
}
