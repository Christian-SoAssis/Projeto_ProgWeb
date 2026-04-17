import { useState, useEffect } from "react"
import { requestRepository } from "@/repositories"
import type { ServiceRequest } from "@/domain/models/request"

export function useRequests() {
    const [requests, setRequests] = useState<ServiceRequest[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        requestRepository.listMine()
            .then(setRequests)
            .catch(() => setError("Erro ao carregar pedidos"))
            .finally(() => setLoading(false))
    }, [])

    return { requests, loading, error }
}
