"use client"

import { useState, useEffect } from "react"
import { apiFetch } from "@/lib/api"
import type { ProfessionalMatch } from "@/types/professional"

export interface SearchParams {
    lat: number | null
    lng: number | null
    q?: string
    categoryId?: string
    radiusKm?: number
}

export function useSearchProfessionals(params: SearchParams) {
    const [results, setResults] = useState<ProfessionalMatch[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (params.lat == null || params.lng == null) return

        const qs = new URLSearchParams({
            lat: String(params.lat),
            lng: String(params.lng),
            radius_km: String(params.radiusKm ?? 20),
        })
        if (params.q) qs.set("q", params.q)
        if (params.categoryId) qs.set("category_id", params.categoryId)

        setLoading(true)
        setError(null)

        apiFetch(`/search/professionals?${qs.toString()}`)
            .then((data: ProfessionalMatch[]) => setResults(data))
            .catch(() => setError("Erro ao buscar profissionais"))
            .finally(() => setLoading(false))
    }, [params.lat, params.lng, params.q, params.categoryId, params.radiusKm])

    return { results, loading, error }
}
