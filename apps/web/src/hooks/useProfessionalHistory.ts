import { useState, useEffect } from "react"
import { apiFetch } from "@/lib/api"

export interface ContractHistoryItem {
  id: string
  request_title: string
  client_name: string
  agreed_cents: number
  completed_at: string
  rating?: number
}

export function useProfessionalHistory() {
  const [history, setHistory] = useState<ContractHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchHistory() {
      try {
        setLoading(true)
        const data = await apiFetch("/professionals/me/history")
        setHistory(data)
      } catch (err: any) {
        setError(err.message || "Erro ao carregar histórico")
      } finally {
        setLoading(false)
      }
    }
    fetchHistory()
  }, [])

  return { history, loading, error }
}
