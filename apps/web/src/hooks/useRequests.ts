import { useState, useEffect } from "react"
import { requestsService } from "@/services/requests.service"
import type { ServiceRequest } from "@/types/request"

export function useRequests() {
    const [requests, setRequests] = useState<ServiceRequest[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        requestsService.listMine()
            .then(setRequests)
            .catch(() => setError("Erro ao carregar pedidos"))
            .finally(() => setLoading(false))
    }, [])

    return { requests, loading, error }
}
