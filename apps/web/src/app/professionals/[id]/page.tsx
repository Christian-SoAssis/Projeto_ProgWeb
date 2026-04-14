"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import { ChevronLeft, Star, DollarSign, ShieldCheck, MapPin, Briefcase } from "lucide-react"
import { apiFetch } from "@/lib/api"

function formatCurrency(cents: number) {
  return (cents / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
}

export default function ProfessionalProfilePage() {
  const params = useParams()
  const router = useRouter()
  const profId = params.id as string
  const [prof, setProf] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      if (!profId) return
      try {
        const data = await apiFetch(`/professionals/${profId}`)
        setProf(data)
      } catch (err: any) {
        toast.error("Erro ao carregar perfil", { description: err.message })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [profId])

  if (loading) {
    return (
      <main className="min-h-screen bg-background pb-20 px-6 max-w-lg mx-auto">
        <div className="pt-6 pb-2">
          <Skeleton className="w-24 h-8 rounded-xl" />
        </div>
        <Card variant="neo-elevated" className="mt-6 border-none rounded-[2.5rem] p-8 space-y-6">
          <div className="flex flex-col items-center gap-4">
            <Skeleton className="w-24 h-24 rounded-3xl" />
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-32" />
          </div>
          <div className="space-y-3 pt-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
          </div>
        </Card>
      </main>
    )
  }

  if (!prof) return null

  return (
    <main className="min-h-screen bg-background pb-20 px-6 max-w-lg mx-auto">
      <div className="pt-6 pb-2">
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="gap-2 text-muted-foreground">
          <ChevronLeft className="w-4 h-4" /> Voltar
        </Button>
      </div>

      <Card variant="neo-elevated" className="mt-6 border-none rounded-[2.5rem] overflow-hidden">
        <div className="relative h-32 bg-primary/10" />
        <CardContent className="px-8 pb-8 -mt-12 flex flex-col items-center">
          <div className="w-24 h-24 neo-elevated rounded-3xl flex items-center justify-center text-4xl bg-background border-4 border-background">
            {prof.name?.[0] || "P"}
          </div>
          
          <div className="mt-4 text-center">
            <h1 className="text-2xl font-black tracking-tight">{prof.name}</h1>
            <div className="flex items-center justify-center gap-2 mt-1">
              <div className="flex items-center gap-1 text-primary">
                <Star className="w-4 h-4 fill-primary" />
                <span className="text-sm font-black font-mono">{prof.reputation_score?.toFixed(1)}</span>
              </div>
              {prof.is_verified && (
                <Badge variant="secondary" className="bg-green-500/10 text-green-600 border-none rounded-lg px-2 py-0.5 text-[10px] font-black uppercase tracking-wider gap-1">
                  <ShieldCheck className="w-3 h-3" /> Verificado
                </Badge>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 w-full mt-8">
            <div className="neo-inset rounded-2xl p-4 flex flex-col items-center gap-1">
              <DollarSign className="w-5 h-5 text-primary" />
              <span className="text-xs font-bold text-muted-foreground">Valor/Hora</span>
              <span className="text-sm font-black">{formatCurrency(prof.hourly_rate_cents || 0)}</span>
            </div>
            <div className="neo-inset rounded-2xl p-4 flex flex-col items-center gap-1">
              <Briefcase className="w-5 h-5 text-primary" />
              <span className="text-xs font-bold text-muted-foreground">Categorias</span>
              <span className="text-sm font-black">{prof.categories?.length || 0}</span>
            </div>
          </div>

          <div className="w-full mt-8 space-y-2">
            <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/60 px-1">Sobre</h3>
            <div className="neo-inset rounded-2xl p-4">
              <p className="text-sm leading-relaxed text-foreground/80 font-medium italic">
                "{prof.bio}"
              </p>
            </div>
          </div>

          <div className="w-full mt-8 space-y-2">
            <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/60 px-1">Especialidades</h3>
            <div className="flex flex-wrap gap-2 text-center items-center justify-center">
              {prof.categories?.map((cat: any) => (
                <Badge 
                  key={cat.id} 
                  variant="neo-elevated"
                  className="rounded-xl border-none font-bold text-xs py-2 px-4"
                  style={{ color: cat.color }}
                >
                  {cat.name}
                </Badge>
              ))}
            </div>
          </div>

          <div className="w-full mt-10">
            <Button 
                variant="neo-elevated" 
                className="w-full h-14 rounded-2xl text-base font-black text-primary gap-2"
                onClick={() => toast.info("Funcionalidade de orçamento em breve!")}
            >
              Solicitar Orçamento
            </Button>
          </div>
        </CardContent>
      </Card>
    </main>
  )
}
