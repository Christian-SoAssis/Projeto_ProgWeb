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
    <main className="min-h-screen bg-background pb-20">
      <DashboardHeader userName={user?.name || "Cliente"} roleLabel="Cliente" />

      <div className="px-6 space-y-8 max-w-2xl mx-auto">
        <section className="mt-4">
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
            />
          </div>
        </section>

        <section className="grid grid-cols-1 gap-4">
          <Button
            variant="neo-elevated"
            className="h-20 rounded-2xl flex justify-between items-center px-6 group"
            onClick={() => router.push("/requests/new")}
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl neo-inset bg-primary/10 flex items-center justify-center">
                <Plus className="w-6 h-6 text-primary" />
              </div>
              <div className="text-left">
                <span className="block font-bold text-lg">Criar Novo Pedido</span>
                <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground opacity-60">
                  Gratuito e rápido
                </span>
              </div>
            </div>
            <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:translate-x-1 transition-transform" />
          </Button>
        </section>

        <section className="space-y-4">
          <div className="flex justify-between items-center px-1">
            <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/80">
              Seus Pedidos Ativos
            </h3>
            <Button variant="link" size="sm" className="text-xs font-bold text-primary px-0">
              Ver todos
            </Button>
          </div>

          <div className="space-y-4">
            {loadingRequests ? (
              [1, 2].map((i) => (
                <Card key={i} variant="neo-elevated" className="border-none rounded-[2rem] p-4">
                  <div className="flex justify-between items-center mb-4">
                    <Skeleton className="h-6 w-32" />
                    <Skeleton className="h-5 w-20 rounded-full" />
                  </div>
                  <div className="flex gap-4">
                    <Skeleton className="h-3 w-20" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                </Card>
              ))
            ) : requests.length === 0 ? (
              <Card variant="neo-elevated" className="border-none rounded-[2rem] p-8 text-center flex flex-col items-center gap-4">
                <div className="w-16 h-16 neo-inset rounded-3xl flex items-center justify-center bg-background/50">
                  <Package className="w-8 h-8 text-muted-foreground" />
                </div>
                <div>
                  <h4 className="font-bold text-lg">Nenhum pedido ainda</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Que tal criar o seu primeiro hoje?
                  </p>
                </div>
                <Button
                  variant="neo-elevated"
                  size="sm"
                  onClick={() => router.push("/requests/new")}
                  className="font-bold text-primary px-6 rounded-xl"
                >
                  Começar
                </Button>
              </Card>
            ) : (
              requests.map((req) => {
                const status = STATUS_CONFIG[req.status] ?? STATUS_CONFIG.open
                return (
                  <Card
                    key={req.id}
                    variant="neo-elevated"
                    className="border-none rounded-[2rem] p-2 hover:translate-y-[-2px] transition-transform cursor-pointer group"
                    onClick={() => router.push(`/requests/${req.id}/matches`)}
                  >
                    <CardHeader className="pb-2">
                      <div className="flex justify-between items-start gap-2">
                        <CardTitle className="text-lg font-bold truncate">{req.title}</CardTitle>
                        <span className={`text-[10px] font-mono font-bold px-3 py-1 rounded-full uppercase shrink-0 ${status.className}`}>
                          {status.label}
                        </span>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex gap-4 text-xs font-medium text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-primary" />
                          {formatDate(req.createdAt)}
                        </div>
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-primary" /> Localizado
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })
            )}
          </div>
        </section>
      </div>

      <section className="px-6 mt-12 max-w-2xl mx-auto">
        <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/80 px-1 mb-4">
          Categorias Populares
        </h3>
        <div className="grid grid-cols-2 gap-4">
          {displayCategories.map((cat) => (
            <Button key={cat.id} variant="neo-elevated" className="h-16 rounded-2xl bg-background font-bold text-sm">
              {cat.name}
            </Button>
          ))}
        </div>
      </section>
    </main>
  )
}
