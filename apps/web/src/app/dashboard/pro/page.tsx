"use client"

import { DashboardHeader } from "@/components/dashboard/DashboardHeader"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MapPin, Star, DollarSign, Briefcase, Zap, AlertCircle } from "lucide-react"
import { useAuth } from "@/context/auth-context"
import { useEffect, useState, useRef } from "react"
import { apiFetch } from "@/lib/api"
import { toast } from "sonner"

function formatCurrency(cents: number): string {
  return (cents / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
}

export default function ProfessionalDashboard() {
  const { user } = useAuth()
  const [metrics, setMetrics] = useState<any>(null)
  const [bids, setBids] = useState<any[]>([])
  const [loadingData, setLoadingData] = useState(true)

  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [locationError, setLocationError] = useState<string | null>(null)
  const [isLocating, setIsLocating] = useState(false)
  const hasAttemptedRef = useRef(false)

  const leads = [
    { id: 1, service: "Vazamento na Cozinha", client: "Maria Oliveira", distance: "2.4 km", budget: "R$ 150-300" },
    { id: 2, service: "Ar condicionado parou", client: "João Pedro", distance: "4.1 km", budget: "R$ 400+" },
    { id: 3, service: "Instalação de Chuveiro", client: "Ana Santos", distance: "1.2 km", budget: "R$ 80-120" },
  ]

  useEffect(() => {
    async function load() {
      try {
        const [met] = await Promise.all([
          apiFetch("/professionals/me/metrics"),
        ])
        setMetrics(met)
        setBids([])
      } catch (err) {
        setMetrics({ reputation_score: 0, total_earnings_cents: 0, completed_jobs: 0, pending_bids: 0 })
      } finally {
        setLoadingData(false)
      }
    }
    load()
  }, [])

  const requestLocation = () => {
    if (!navigator.geolocation) {
      setLocationError("Geolocalização não suportada pelo navegador.")
      return
    }

    setIsLocating(true)
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude })
        setLocationError(null)
        setIsLocating(false)
      },
      (err) => {
        setIsLocating(false)
        setLocationError("Não foi possível acessar sua localização.")
      },
      { timeout: 10000 }
    )
  }

  useEffect(() => {
    if (!hasAttemptedRef.current) {
        hasAttemptedRef.current = true
        requestLocation()
    }
  }, [])

  return (
    <main className="min-h-screen bg-background pb-20">
      <DashboardHeader userName={user?.name || "Profissional"} roleLabel="Profissional" />

      <div className="px-6 space-y-8 max-w-2xl mx-auto">
        {/* Stats Grid */}
        <section className="mt-4 grid grid-cols-2 gap-4">
          <Card variant="neo-elevated" className="border-none rounded-3xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-center text-primary">
              <Star className="w-5 h-5 fill-primary/20" />
              <span className="text-xl font-black">
                {metrics?.reputation_score?.toFixed(1) ?? "—"}
              </span>
            </div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground opacity-70">Avaliação Média</span>
          </Card>
          <Card variant="neo-elevated" className="border-none rounded-3xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-center text-secondary">
              <DollarSign className="w-5 h-5" />
              <span className="text-sm font-black truncate">
                {metrics ? formatCurrency(metrics.total_earnings_cents) : "R$ —"}
              </span>
            </div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground opacity-70">Ganhos Totais</span>
          </Card>
        </section>

        {/* Location Status */}
        {(locationError || isLocating) && (
          <section>
            <div className={`neo-inset rounded-2xl p-4 flex items-center gap-3 ${locationError ? 'text-destructive' : 'text-primary'}`}>
              {isLocating ? (
                <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              ) : (
                <AlertCircle className="w-5 h-5" />
              )}
              <span className="text-xs font-bold">
                {isLocating ? "Obtendo sua localização para filtrar serviços próximos..." : locationError}
              </span>
            </div>
          </section>
        )}

        {/* Available Leads */}
        <section className="space-y-4">
          <div className="flex justify-between items-center px-1">
            <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/80 flex items-center gap-2">
              <Zap className="w-4 h-4 text-primary fill-primary/20" /> Oportunidades Próximas
            </h3>
            <Button variant="link" size="sm" className="text-xs font-bold text-primary px-0">Ver mapa</Button>
          </div>

          <div className="space-y-4">
            {/* TODO: conectar a GET /search/professionals quando tiver busca por localização */}
            {/* Os leads reais virão de GET /requests (pedidos abertos na área do profissional) */}
            {leads.map((lead) => (
              <Card key={lead.id} variant="neo-elevated" className="border-none rounded-[2rem] p-4 hover:translate-y-[-2px] transition-transform cursor-pointer group">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="text-lg font-bold group-hover:text-primary transition-colors">{lead.service}</h4>
                    <p className="text-xs font-medium text-muted-foreground">{lead.client}</p>
                  </div>
                  <div className="bg-background neo-inset px-3 py-2 rounded-xl text-xs font-black text-secondary">
                    {lead.budget}
                  </div>
                </div>
                
                <div className="flex items-center gap-4 border-t border-muted/20 pt-3">
                  <div className="flex items-center gap-1 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                    <MapPin className="w-3 h-3 text-primary" /> {lead.distance}
                  </div>
                  <div className="flex items-center gap-1 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                    <Briefcase className="w-3 h-3 text-primary" /> Manutenção
                  </div>
                  <Button variant="neo-elevated" size="sm" className="ml-auto h-8 px-4 rounded-xl text-[10px] font-bold text-primary shadow-none">
                    Dar Lance
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </section>

        {/* Verification Alert (Mock) */}
        <section>
          <div className="neo-elevated rounded-3xl p-6 bg-primary/5 flex gap-4 items-center">
            <div className="w-12 h-12 rounded-2xl neo-inset flex items-center justify-center bg-background/50">
              <Zap className="w-6 h-6 text-primary animate-pulse" />
            </div>
            <div className="flex-1">
              <h5 className="font-bold text-sm">Aumente sua visibilidade</h5>
              <p className="text-xs text-muted-foreground">Torne-se um profissional verificado para ganhar preferência nos lances.</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
  )
}
