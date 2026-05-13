import { apiFetch } from "@/lib/api";
import { Review } from "../../domain/models/review";
import { ReviewRepository, CreateReviewPayload } from "../../domain/repositories/review.repository";

export class ReviewRepositoryImpl implements ReviewRepository {
    private mapToEntity(data: any): Review {
        return {
            id: data.id,
            contractId: data.contract_id,
            reviewerId: data.reviewer_id,
            revieweeId: data.reviewee_id,
            rating: data.rating,
            text: data.text,
            scorePunctuality: data.score_punctuality,
            scoreQuality: data.score_quality,
            scoreCleanliness: data.score_cleanliness,
            scoreCommunication: data.score_communication,
            isAuthentic: data.is_authentic,
            createdAt: data.created_at,
        };
    }

    async create(payload: CreateReviewPayload): Promise<Review> {
        const data = await apiFetch("/reviews", {
            method: "POST",
            body: JSON.stringify({
                contract_id: payload.contractId,
                rating: payload.rating,
                text: payload.text,
            }),
        });
        return this.mapToEntity(data);
    }

    async listByProfessional(professionalId: string): Promise<Review[]> {
        const data = await apiFetch(`/professionals/${professionalId}/reviews`);
        return data.map(this.mapToEntity.bind(this));
    }
}
