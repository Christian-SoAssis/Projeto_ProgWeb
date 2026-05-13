"use client"

import { useState, useEffect, useCallback } from "react"
import { Bid } from "@/domain/models/bid"
import { bidRepository } from "@/repositories"

export function useBids(requestId: string) {
    const [bids, setBids] = useState<Bid[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const reload = useCallback(() => {
        if (!requestId) return
        setLoading(true)
        bidRepository
            .listByRequest(requestId)
            .then(setBids)
            .catch(() => setError("Erro ao carregar lances"))
            .finally(() => setLoading(false))
    }, [requestId])

    useEffect(() => {
        reload()
    }, [reload])

    return { bids, loading, error, reload }
}
