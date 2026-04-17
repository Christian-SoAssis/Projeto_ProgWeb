import { apiFetch } from "@/lib/api";
import { Professional, ProfessionalMetrics } from "../../domain/models/professional";
import { ProfessionalRepository } from "../../domain/repositories/professional.repository";

export class ProfessionalRepositoryImpl implements ProfessionalRepository {
    private mapToEntity(data: any): Professional {
        return {
            id: data.id,
            userId: data.user_id,
            name: data.name,
            email: data.email,
            bio: data.bio,
            latitude: data.latitude,
            longitude: data.longitude,
            serviceRadiusKm: data.service_radius_km,
            hourlyRateCents: data.hourly_rate_cents,
            reputationScore: data.reputation_score,
            isVerified: data.is_verified,
            categories: (data.categories || []).map((cat: any) => ({
                id: cat.id,
                name: cat.name,
                color: cat.color,
            })),
        };
    }

    private mapMetrics(data: any): ProfessionalMetrics {
        return {
            totalEarningsCents: data.total_earnings_cents,
            completedJobs: data.completed_jobs,
            pendingBids: data.pending_bids,
            reputationScore: data.reputation_score,
            conversionRate: data.conversion_rate,
        };
    }

    async getById(id: string): Promise<Professional> {
        const data = await apiFetch(`/professionals/${id}`);
        return this.mapToEntity(data);
    }

    async getMetrics(): Promise<ProfessionalMetrics> {
        const data = await apiFetch("/professionals/panel/metrics");
        return this.mapMetrics(data);
    }

    async register(payload: FormData): Promise<Professional> {
        const data = await apiFetch("/professionals", {
            method: "POST",
            body: payload, // FormData headers are multipart/form-data
        });
        return this.mapToEntity(data);
    }
}
