export interface ServiceRequest {
    id: string;
    clientId: string;
    categoryId: string;
    title: string;
    description?: string;
    latitude: number;
    longitude: number;
    urgency: 'immediate' | 'scheduled' | 'flexible';
    budgetCents?: number;
    status: 'open' | 'matched' | 'in_progress' | 'done' | 'cancelled';
    createdAt: string;
    updatedAt: string;
    images: RequestImage[];
}

export interface RequestImage {
    id: string;
    requestId: string;
    url: string;
    contentType: string;
    sizeBytes: number;
    analyzed: boolean;
    createdAt: string;
}
