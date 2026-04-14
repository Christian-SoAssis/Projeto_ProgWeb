import { useState, useEffect } from "react"
import { professionalsService } from "@/services/professionals.service"
import type { ProfessionalMetrics } from "@/types/professional"

const FALLBACK: ProfessionalMetrics = {
    reputation_score: 0,
    total_earnings_cents: 0,
    completed_jobs: 0,
    pending_bids: 0,
    conversion_rate: 0,
}

export function useProfessionalMetrics() {
    const [metrics, setMetrics] = useState<ProfessionalMetrics | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        professionalsService.getMyMetrics()
            .then(setMetrics)
            .catch(() => setMetrics(FALLBACK))
            .finally(() => setLoading(false))
    }, [])

    return { metrics, loading }
}
