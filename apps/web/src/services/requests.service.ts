import { apiFetch } from "@/lib/api"
import type { ServiceRequest, CreateRequestPayload } from "@/types/request"
import type { ProfessionalMatch } from "@/types/professional"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export const requestsService = {
    async listMine(limit = 10): Promise<ServiceRequest[]> {
        return apiFetch(`/requests?client_only=true&limit=${limit}`)
    },

    async getById(id: string): Promise<ServiceRequest> {
        return apiFetch(`/requests/${id}`)
    },

    async getMatches(id: string): Promise<ProfessionalMatch[]> {
        return apiFetch(`/requests/${id}/matches`)
    },

    async create(payload: CreateRequestPayload): Promise<ServiceRequest> {
        const token = typeof window !== "undefined"
            ? localStorage.getItem("access_token")
            : null

        const formData = new FormData()
        formData.append("title", payload.title)
        if (payload.description) formData.append("description", payload.description)
        formData.append("category_id", payload.category_id)
        formData.append("urgency", payload.urgency)
        formData.append("latitude", String(payload.latitude))
        formData.append("longitude", String(payload.longitude))
        if (payload.budget_cents) formData.append("budget_cents", String(payload.budget_cents))
        payload.images?.forEach((img) => formData.append("images", img))

        const response = await fetch(`${BASE_URL}/requests`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
            body: formData,
        })

        if (!response.ok) {
            const err = await response.json().catch(() => ({}))
            throw new Error(err.detail || "Erro ao criar pedido")
        }

        return response.json()
    },
}
