export type RequestStatus = "open" | "matched" | "in_progress" | "done" | "cancelled"
export type RequestUrgency = "immediate" | "scheduled" | "flexible"

export interface ServiceRequest {
    id: string
    title: string
    description?: string
    status: RequestStatus
    urgency: RequestUrgency
    category_id: string
    budget_cents?: number
    latitude?: number
    longitude?: number
    created_at: string
    updated_at: string
}

export interface CreateRequestPayload {
    title: string
    description?: string
    category_id: string
    urgency: RequestUrgency
    budget_cents?: number
    latitude: number
    longitude: number
    images?: File[]
}
