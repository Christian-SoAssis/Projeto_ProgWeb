"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import { ChevronLeft, MapPin, Star, DollarSign, Zap } from "lucide-react"
import { apiFetch } from "@/lib/api"

function formatCurrency(cents: number) {
  return (cents / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
}

export default function MatchesPage() {
  const params = useParams()
  const router = useRouter()
  const requestId = params.id as string
  const [matches, setMatches] = useState<any[]>([])
  const [request, setRequest] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      if (!requestId) return
      try {
        const [req, matchList] = await Promise.all([
          apiFetch(`/requests/${requestId}`),
          apiFetch(`/requests/${requestId}/matches`),
        ])
        setRequest(req)
        setMatches(matchList)
      } catch (err: any) {
        toast.error("Erro ao carregar matches", { description: err.message })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [requestId])

  return (
    <main className="min-h-screen bg-background pb-20 px-6 max-w-lg mx-auto">
      <div className="pt-6 pb-2">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard/client")} className="gap-2 text-muted-foreground">
          <ChevronLeft className="w-4 h-4" /> Dashboard
        </Button>
      </div>

      <div className="mb-6">
        <h1 className="text-2xl font-extrabold tracking-tight">
          Profissionais <span className="text-primary italic">Disponíveis</span>
        </h1>
        {request && (
          <p className="text-sm text-muted-foreground mt-1 font-medium">{request.title}</p>
        )}
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} variant="neo-elevated" className="border-none rounded-[2rem] p-4">
              <div className="flex gap-4 items-center">
                <Skeleton className="w-14 h-14 rounded-2xl" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : matches.length === 0 ? (
        <Card variant="neo-elevated" className="border-none rounded-[2rem] p-8 text-center flex flex-col items-center gap-4">
          <div className="w-16 h-16 neo-inset rounded-3xl flex items-center justify-center bg-background/50">
            <Zap className="w-8 h-8 text-muted-foreground" />
          </div>
          <div>
            <h3 className="font-bold text-lg">Nenhum profissional encontrado</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Tente ampliar o raio de busca ou mudar a categoria.
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {matches.map((prof: any) => (
            <Card key={prof.id} variant="neo-elevated" className="border-none rounded-[2rem] p-4 hover:translate-y-[-2px] transition-transform cursor-pointer group">
              <div className="flex gap-4 items-start">
                <div className="w-14 h-14 neo-inset rounded-2xl flex items-center justify-center text-2xl bg-background/50 shrink-0">
                  🔧
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start gap-2">
                    <h4 className="font-bold text-base truncate">{prof.bio?.slice(0, 40) || "Profissional"}</h4>
                    <div className="flex items-center gap-1 shrink-0 text-primary">
                      <Star className="w-3 h-3 fill-primary" />
                      <span className="text-xs font-black font-mono">{prof.reputation_score?.toFixed(1)}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 mt-2 text-xs font-medium text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-primary" />
                      {prof.distance_km?.toFixed(1)} km
                    </div>
                    {prof.hourly_rate_cents && (
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-3 h-3 text-primary" />
                        {formatCurrency(prof.hourly_rate_cents)}/h
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-muted/20 flex gap-2">
                <Button
                  variant="neo-elevated"
                  className="flex-1 h-10 rounded-xl text-xs font-bold text-primary"
                  onClick={() => toast.info("Em breve: envio de orçamento pelo profissional")}
                >
                  Ver Perfil
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </main>
  )
}
