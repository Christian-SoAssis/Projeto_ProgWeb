import { useState, useEffect } from "react"
import { apiFetch } from "@/lib/api"

export interface AISummaryResponse {
  summary: string
  generated_at: string
}

export function useProfessionalAISummary() {
  const [data, setData] = useState<AISummaryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchSummary() {
      try {
        setLoading(true)
        const response = await apiFetch("/professionals/me/ai-summary")
        setData(response)
      } catch (err: any) {
        setError(err.message || "Erro ao gerar resumo IA")
      } finally {
        setLoading(false)
      }
    }
    fetchSummary()
  }, [])

  return { data, loading, error }
}
