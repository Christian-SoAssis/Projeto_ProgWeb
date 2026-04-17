export interface Bid {
    id: string;
    requestId: string;
    professionalId: string;
    priceCents: number;
    estimatedHours?: number;
    message?: string;
    status: 'pending' | 'accepted' | 'rejected' | 'cancelled';
    createdAt: string;
}

export type BidStatus = Bid['status'];
