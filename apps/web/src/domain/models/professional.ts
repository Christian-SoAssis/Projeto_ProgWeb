import { Category } from "./category";
export type { Category };

export interface Professional {
    id: string;
    userId: string;
    name?: string;
    email?: string;
    bio: string;
    latitude: number;
    longitude: number;
    serviceRadiusKm: number;
    hourlyRateCents?: number;
    reputationScore: number;
    isVerified: boolean;
    categories: Category[];
}

export interface ProfessionalMatch extends Professional {
    distanceKm?: number;
}

export interface ProfessionalMetrics {
    totalEarningsCents: number;
    completedJobs: number;
    pendingBids: number;
    reputationScore: number;
    conversionRate: number;
}
