import { apiFetch } from "@/lib/api";
import { Contract } from "../../domain/models/contract";
import { ContractRepository } from "../../domain/repositories/contract.repository";

export class ContractRepositoryImpl implements ContractRepository {
    private mapToEntity(data: any): Contract {
        return {
            id: data.id,
            requestId: data.request_id,
            professionalId: data.professional_id,
            clientId: data.client_id,
            agreedCents: data.agreed_cents,
            status: data.status,
            startedAt: data.started_at,
            completedAt: data.completed_at,
        };
    }

    async getById(id: string): Promise<Contract> {
        const data = await apiFetch(`/contracts/${id}`);
        return this.mapToEntity(data);
    }
}
