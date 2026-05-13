import { Review } from "../models/review";

export interface CreateReviewPayload {
    contractId: string;
    rating: number;
    text: string;
}

export interface ReviewRepository {
    create(payload: CreateReviewPayload): Promise<Review>;
    listByProfessional(professionalId: string): Promise<Review[]>;
}
