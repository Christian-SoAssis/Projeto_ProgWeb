import { ServiceRequest } from "../models/request";

export interface CreateRequestPayload {
    title: string;
    description?: string;
    category_id: string;
    urgency: string;
    latitude: number;
    longitude: number;
    budget_cents?: number;
    images?: File[];
}

export interface RequestRepository {
    listMine(limit?: number): Promise<ServiceRequest[]>;
    getById(id: string): Promise<ServiceRequest>;
    create(payload: CreateRequestPayload): Promise<ServiceRequest>;
}
