import { apiFetch } from "@/lib/api"
import type { ProfessionalMetrics } from "@/types/professional"

export const professionalsService = {
    async getMyMetrics(): Promise<ProfessionalMetrics> {
        return apiFetch("/professionals/me/metrics")
    },
}
