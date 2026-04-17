import { Bid } from "../models/bid";

export interface CreateBidPayload {
    requestId: string;
    priceCents: number;
    estimatedHours?: number;
    message?: string;
}

export interface BidRepository {
    create(payload: CreateBidPayload): Promise<Bid>;
    updateStatus(bidId: string, status: string): Promise<{ bid: Bid; contract?: any }>;
    listByRequest(requestId: string): Promise<Bid[]>;
}
