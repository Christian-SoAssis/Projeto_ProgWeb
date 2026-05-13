"use client"

import { useState, useEffect } from "react"
import { ServiceRequest } from "@/domain/models/request"
import { apiFetch } from "@/lib/api"

export function useAvailableRequests() {
    const [requests, setRequests] = useState<ServiceRequest[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        apiFetch("/requests")
            .then((data: any[]) =>
                setRequests(
                    data.map((r) => ({
                        id: r.id,
                        clientId: r.client_id,
                        categoryId: r.category_id,
                        title: r.title,
                        description: r.description,
                        status: r.status,
                        urgency: r.urgency,
                        budgetCents: r.budget_cents,
                        latitude: r.latitude,
                        longitude: r.longitude,
                        images: r.images ?? [],
                        createdAt: r.created_at,
                        updatedAt: r.updated_at,
                    }))
                )
            )
            .catch(() => setError("Erro ao carregar oportunidades"))
            .finally(() => setLoading(false))
    }, [])

    return { requests, loading, error }
}
