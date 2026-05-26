"use client"

import { DashboardHeader } from "@/components/dashboard/DashboardHeader"
import { useAuth } from "@/presentation/hooks/use-auth"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { User, Sparkles, History, Star, Clock, CheckCircle2, Award } from "lucide-react"
import { useProfessionalHistory } from "@/hooks/useProfessionalHistory"
import { useProfessionalAISummary } from "@/hooks/useProfessionalAISummary"
import { formatCurrency, formatDate } from "@/lib/formatters"
import { Skeleton } from "@/components/ui/skeleton"

export default function ProProfile() {
  const { user } = useAuth()
  const { history, loading: loadingHistory } = useProfessionalHistory()
  const { data: aiSummary, loading: loadingAI } = useProfessionalAISummary()

  return (
    <main className="min-h-screen bg-background pb-20">
      <DashboardHeader userName={user?.name || "Profissional"} roleLabel="Perfil Profissional" />

      <div className="px-6 space-y-8 max-w-2xl mx-auto mt-6">
        
        {/* Basic Info */}
        <section>
          <Card variant="neo-elevated" className="border-none rounded-3xl p-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full neo-inset flex items-center justify-center bg-background/50">
                <User className="w-8 h-8 text-secondary" />
              </div>
              <div>
                <h3 className="font-bold text-lg">{user?.name}</h3>
                <p className="text-sm font-medium text-primary">Profissional Verificado</p>
              </div>
            </div>
          </Card>
        </section>

        {/* AI Summary */}
        <section>
          <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/80 mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-500 fill-purple-500/20" /> 
            Resumo de Avaliações (IA)
          </h3>
          <Card variant="neo-elevated" className="border-none rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Award className="w-24 h-24 text-purple-500" />
            </div>
            
            {loadingAI ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-4/6" />
              </div>
            ) : (
              <div className="relative z-10">
                <p className="text-sm font-medium leading-relaxed">
                  {aiSummary?.summary || "Você ainda não possui avaliações suficientes para gerar um resumo."}
                </p>
                {aiSummary?.generated_at && (
                  <p className="text-[10px] text-muted-foreground mt-4 uppercase font-bold">
                    Gerado em: {formatDate(aiSummary.generated_at)}
                  </p>
                )}
              </div>
            )}
          </Card>
        </section>

        {/* Service History */}
        <section>
          <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/80 mb-3 flex items-center gap-2">
            <History className="w-4 h-4 text-primary" /> 
            Histórico de Pedidos Atendidos
          </h3>
          
          <div className="space-y-4">
            {loadingHistory ? (
              [1, 2].map(i => (
                <Card key={i} variant="neo-elevated" className="border-none rounded-3xl p-4">
                  <Skeleton className="h-5 w-1/2 mb-2" />
                  <Skeleton className="h-4 w-1/3" />
                </Card>
              ))
            ) : history.length === 0 ? (
              <Card variant="neo-elevated" className="border-none rounded-3xl p-8 text-center text-muted-foreground">
                Você ainda não tem serviços concluídos.
              </Card>
            ) : (
              history.map(item => (
                <Card key={item.id} variant="neo-elevated" className="border-none rounded-3xl p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-bold">{item.request_title}</h4>
                    <span className="bg-green-500/10 text-green-600 px-2 py-1 rounded-lg text-xs font-bold flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> {formatCurrency(item.agreed_cents)}
                    </span>
                  </div>
                  
                  <p className="text-xs text-muted-foreground font-medium mb-3">
                    Cliente: {item.client_name}
                  </p>
                  
                  <div className="flex items-center gap-4 text-[10px] uppercase font-bold text-muted-foreground border-t border-muted/20 pt-3">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {formatDate(item.completed_at)}
                    </span>
                    {item.rating && (
                      <span className="flex items-center gap-1 text-yellow-500">
                        <Star className="w-3 h-3 fill-yellow-500" /> {item.rating}
                      </span>
                    )}
                  </div>
                </Card>
              ))
            )}
          </div>
        </section>
      </div>
    </main>
  )
}
