import { Professional, ProfessionalMetrics } from "../models/professional";

export interface ProfessionalRepository {
    getById(id: string): Promise<Professional>;
    getMetrics(): Promise<ProfessionalMetrics>;
    register(payload: FormData): Promise<Professional>;
}
