def calculate_reputation_score(
    avg_quality: float,
    avg_punctuality: float,
    avg_communication: float,
    avg_cleanliness: float,
    completed_jobs: int,
) -> float:
    """Calcula reputation_score na escala 0-5."""
    jobs_factor = min(completed_jobs / 50.0, 1.0)
    raw = (
        0.30 * avg_quality
        + 0.25 * avg_punctuality
        + 0.20 * avg_communication
        + 0.15 * avg_cleanliness
        + 0.10 * jobs_factor
    )
    return round(raw * 5.0, 4)
