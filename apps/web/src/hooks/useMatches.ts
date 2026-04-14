import { useState, useEffect } from "react"
import { requestsService } from "@/services/requests.service"
import type { ServiceRequest } from "@/types/request"
import type { ProfessionalMatch } from "@/types/professional"

export function useMatches(requestId: string) {
    const [request, setRequest] = useState<ServiceRequest | null>(null)
    const [matches, setMatches] = useState<ProfessionalMatch[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!requestId) return
        Promise.all([
            requestsService.getById(requestId),
            requestsService.getMatches(requestId),
        ])
            .then(([req, matchList]) => {
                setRequest(req)
                setMatches(matchList)
            })
            .catch((err) => setError(err.message || "Erro ao carregar matches"))
            .finally(() => setLoading(false))
    }, [requestId])

    return { request, matches, loading, error }
}
