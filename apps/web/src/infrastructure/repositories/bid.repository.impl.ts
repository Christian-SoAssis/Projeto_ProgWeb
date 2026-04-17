import { apiFetch } from "@/lib/api";
import { Bid, BidStatus } from "../../domain/models/bid";
import { BidRepository, CreateBidPayload } from "../../domain/repositories/bid.repository";

export class BidRepositoryImpl implements BidRepository {
    private mapToEntity(data: any): Bid {
        return {
            id: data.id,
            requestId: data.request_id,
            professionalId: data.professional_id,
            priceCents: data.price_cents,
            estimatedHours: data.estimated_hours,
            message: data.message,
            status: data.status,
            createdAt: data.created_at,
        };
    }

    async create(payload: CreateBidPayload): Promise<Bid> {
        const data = await apiFetch("/bids", {
            method: "POST",
            body: JSON.stringify({
                request_id: payload.requestId,
                price_cents: payload.priceCents,
                estimated_hours: payload.estimatedHours,
                message: payload.message,
            }),
        });
        return this.mapToEntity(data);
    }

    async updateStatus(bidId: string, status: BidStatus): Promise<{ bid: Bid; contract?: any }> {
        const data = await apiFetch(`/bids/${bidId}`, {
            method: "PATCH",
            body: JSON.stringify({ status }),
        });
        return {
            bid: this.mapToEntity(data.bid),
            contract: data.contract, // Contract could also be mapped if needed
        };
    }

    async listByRequest(requestId: string): Promise<Bid[]> {
        const data = await apiFetch(`/requests/${requestId}/bids`);
        return data.map(this.mapToEntity);
    }
}
