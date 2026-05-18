export interface Notification {
    id: string;
    type: string;
    payload: Record<string, any>;
    readAt: string | null;
    createdAt: string;
}
