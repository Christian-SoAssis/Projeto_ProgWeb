import { useState, useEffect } from "react"
import { professionalRepository } from "@/repositories"
import type { ProfessionalMetrics } from "@/domain/models/professional"

const FALLBACK: ProfessionalMetrics = {
    reputationScore: 0,
    totalEarningsCents: 0,
    completedJobs: 0,
    pendingBids: 0,
    conversionRate: 0,
}

export function useProfessionalMetrics() {
    const [metrics, setMetrics] = useState<ProfessionalMetrics | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        professionalRepository.getMetrics()
            .then(setMetrics)
            .catch(() => setMetrics(FALLBACK))
            .finally(() => setLoading(false))
    }, [])

    return { metrics, loading }
}
