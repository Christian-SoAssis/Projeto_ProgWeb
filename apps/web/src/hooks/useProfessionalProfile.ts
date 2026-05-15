import { useState, useEffect } from "react"
import { apiFetch } from "@/lib/api"

export interface ProfessionalProfile {
  id: string
  bio: string
  location: string
  hourly_rate_cents: number
  is_verified: boolean
  reputation_score: number
  categories: { id: string, name: string, slug: string }[]
}

export function useProfessionalProfile() {
  const [profile, setProfile] = useState<ProfessionalProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await apiFetch("/professionals/me")
        setProfile(data)
      } catch (err: any) {
        setError(err.message || "Erro ao carregar perfil do profissional")
      } finally {
        setLoading(false)
      }
    }
    fetchProfile()
  }, [])

  return { profile, loading, error }
}
