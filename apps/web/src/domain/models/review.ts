export interface Review {
    id: string;
    contractId: string;
    reviewerId: string;
    revieweeId: string;
    rating: number;
    text: string;
    scorePunctuality?: number;
    scoreQuality?: number;
    scoreCleanliness?: number;
    scoreCommunication?: number;
    isAuthentic: boolean;
    createdAt: string;
}
