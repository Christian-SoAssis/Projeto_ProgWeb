export interface ProfessionalMatch {
    id: string
    user_id: string
    bio: string
    latitude: number
    longitude: number
    service_radius_km: number
    hourly_rate_cents?: number
    reputation_score: number
    is_verified: boolean
    distance_km?: number
}

export interface ProfessionalMetrics {
    total_earnings_cents: number
    completed_jobs: number
    pending_bids: number
    reputation_score: number
    conversion_rate: number
}
