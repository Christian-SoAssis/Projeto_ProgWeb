export interface Contract {
    id: string;
    requestId: string;
    professionalId: string;
    clientId: string;
    agreedCents: number;
    status: 'active' | 'completed' | 'disputed' | 'cancelled';
    startedAt: string;
    completedAt?: string;
}
