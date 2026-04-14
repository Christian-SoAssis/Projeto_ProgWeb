import { useState, useEffect } from "react"

export interface GeolocationState {
    latitude: number | null
    longitude: number | null
    isLocating: boolean
    error: string | null
}

export function useGeolocation(autoRequest = true): GeolocationState {
    const [latitude, setLatitude] = useState<number | null>(null)
    const [longitude, setLongitude] = useState<number | null>(null)
    const [isLocating, setIsLocating] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!autoRequest) return
        if (typeof window === "undefined" || !navigator.geolocation) {
            setError("Geolocalização não suportada.")
            return
        }

        setIsLocating(true)
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                setLatitude(pos.coords.latitude)
                setLongitude(pos.coords.longitude)
                setIsLocating(false)
            },
            () => {
                setError("Não foi possível acessar sua localização.")
                setIsLocating(false)
            },
            { timeout: 10000 }
        )
    }, [autoRequest])

    return { latitude, longitude, isLocating, error }
}
