"use client"

import { useRouter } from "next/navigation"
import { DashboardHeader } from "@/components/dashboard/DashboardHeader"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Search, Plus, MapPin, Clock, ArrowRight, Package } from "lucide-react"
import { useAuth } from "@/context/auth-context"
import { useRequests } from "@/hooks/useRequests"
import { useCategories } from "@/hooks/useCategories"
import { formatDate } from "@/lib/formatters"
import type { RequestStatus } from "@/types/request"

const STATUS_CONFIG: Record<RequestStatus, { label: string; className: string }> = {
  open: { label: "Aberto", className: "bg-primary/20 text-primary" },
  matched: { label: "Com bids", className: "bg-blue-500/20 text-blue-600" },
  in_progress: { label: "Em andamento", className: "bg-yellow-500/20 text-yellow-700" },
  done: { label: "Concluído", className: "bg-green-500/20 text-green-700" },
  cancelled: { label: "Cancelado", className: "bg-destructive/20 text-destructive" },
}

const FALLBACK_CATEGORIES = [
  { id: "1", name: "Limpeza" },
  { id: "2", name: "Reformas" },
  { id: "3", name: "Elétrica" },
  { id: "4", name: "Pintura" },
]

export default function ClientDashboard() {
  const { user } = useAuth()
  const router = useRouter()
  const { requests, loading: loadingRequests } = useRequests()
  const { categories } = useCategories()

  const displayCategories = categories.length > 0
    ? categories.slice(0, 4)
    : FALLBACK_CATEGORIES

  return (
    <main className="min-h-screen bg-background pb-28">
      <DashboardHeader userName={user?.name || "Cliente"} roleLabel="Cliente" />

      <div className="px-6 space-y-6 max-w-md mx-auto pt-4">
        {/* Saudação e Busca */}
        <section>
          <h1 className="text-2xl font-black tracking-tight text-foreground/90">
            Olá, <span className="text-primary italic">{user?.name?.split(" ")[0] || "Usuário"}!</span>
          </h1>
          <p className="text-sm font-medium text-muted-foreground mt-1">
            Do que você precisa hoje?
          </p>
        </section>

        <section>
          <div className="neo-inset rounded-2xl flex items-center px-4 py-1 bg-background group focus-within:ring-2 ring-primary/20 transition-all">
            <Search className="w-5 h-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
            <Input
              placeholder="Ex: Encanador, Eletricista..."
              className="border-none shadow-none focus-visible:ring-0 bg-transparent h-14 text-base font-semibold"
              onClick={() => router.push("/search")}
            />
          </div>
        </section>

        {/* Categorias */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground/80">
              Categorias Populares
            </h3>
            <Button variant="link" size="sm" className="text-[10px] font-bold text-primary px-0">
              Ver todas
            </Button>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {displayCategories.map((cat) => (
              <Button 
                key={cat.id} 
                variant="neo-elevated" 
                className="h-14 rounded-[1rem] bg-background font-bold text-xs"
                onClick={() => router.push(`/search?categoryId=${cat.id}`)}
              >
                {cat.name}
              </Button>
            ))}
          </div>
        </section>

        {/* Pedidos Ativos (Horizontal Scroll) */}
        <section className="pt-2">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground/80">
              Seus Pedidos Ativos
            </h3>
          </div>

          <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory hide-scrollbar -mx-6 px-6">
            {loadingRequests ? (
              [1, 2].map((i) => (
                <Card key={i} variant="neo-elevated" className="border-none rounded-[1.5rem] p-4 min-w-[260px] snap-center shrink-0">
                  <div className="flex justify-between items-center mb-4">
                    <Skeleton className="h-5 w-24" />
                    <Skeleton className="h-4 w-16 rounded-full" />
                  </div>
                  <Skeleton className="h-3 w-32" />
                </Card>
              ))
            ) : requests.length === 0 ? (
              <Card variant="neo-elevated" className="border-none rounded-[1.5rem] p-6 text-center flex flex-col items-center gap-3 w-full shrink-0">
                <div className="w-12 h-12 neo-inset rounded-2xl flex items-center justify-center bg-background/50">
                  <Package className="w-6 h-6 text-muted-foreground" />
                </div>
                <div>
                  <h4 className="font-bold text-sm">Nenhum pedido ainda</h4>
                  <p className="text-xs text-muted-foreground mt-1">Crie o primeiro usando o botão abaixo.</p>
                </div>
              </Card>
            ) : (
              requests.map((req) => {
                const status = STATUS_CONFIG[req.status] ?? STATUS_CONFIG.open
                return (
                  <Card
                    key={req.id}
                    variant="neo-elevated"
                    className="border-none rounded-[1.5rem] p-4 min-w-[260px] max-w-[280px] snap-center shrink-0 hover:translate-y-[-2px] transition-transform cursor-pointer"
                    onClick={() => router.push(`/requests/${req.id}/matches`)}
                  >
                    <div className="flex justify-between items-start gap-3 mb-3">
                      <h4 className="text-base font-bold truncate flex-1">{req.title}</h4>
                      <span className={`text-[9px] font-mono font-bold px-2.5 py-1 rounded-md uppercase shrink-0 ${status.className}`}>
                        {status.label}
                      </span>
                    </div>
                    <div className="flex justify-between items-end">
                      <div className="space-y-1">
                        <div className="flex items-center gap-1.5 text-[10px] font-bold text-muted-foreground">
                          <Clock className="w-3 h-3 text-primary" />
                          {formatDate(req.createdAt)}
                        </div>
                        <div className="flex items-center gap-1.5 text-[10px] font-bold text-muted-foreground">
                          <MapPin className="w-3 h-3 text-primary" /> Localizado
                        </div>
                      </div>
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <ArrowRight className="w-4 h-4 text-primary" />
                      </div>
                    </div>
                  </Card>
                )
              })
            )}
          </div>
        </section>
      </div>

      {/* Floating Action Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          variant="neo-elevated"
          className="w-16 h-16 rounded-[1.5rem] bg-primary text-primary-foreground shadow-xl flex items-center justify-center group"
          onClick={() => router.push("/requests/new")}
        >
          <Plus className="w-8 h-8 group-hover:scale-110 transition-transform" />
        </Button>
      </div>

      <style jsx global>{`
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </main>
  )
}
