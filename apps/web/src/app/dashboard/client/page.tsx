"use client"

import { DashboardHeader } from "@/components/dashboard/DashboardHeader"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Search, Plus, MapPin, Clock, ArrowRight } from "lucide-react"
import { useAuth } from "@/context/auth-context"

export default function ClientDashboard() {
  const { user } = useAuth()
  const activeRequests = [
    { id: 1, title: "Reforma Banheiro", status: "Orçamentos (3)", date: "Há 2 dias" },
    { id: 2, title: "Pintura de Fachada", status: "Em análise", date: "Há 5 horas" },
  ]

  return (
    <main className="min-h-screen bg-background pb-20">
      <DashboardHeader userName={user?.name || "Cliente"} roleLabel="Cliente" />

      <div className="px-6 space-y-8 max-w-2xl mx-auto">
        {/* Welcome Section */}
        <section className="mt-4">
          <h1 className="text-2xl font-black tracking-tight text-foreground/90">
            Olá, <span className="text-primary italic">{user?.name?.split(" ")[0] || "Usuário"}!</span>
          </h1>
          <p className="text-sm font-medium text-muted-foreground mt-1">
            Do que você precisa hoje?
          </p>
        </section>

        {/* Search Bar */}
        <section>
          <div className="neo-inset rounded-2xl flex items-center px-4 py-1 bg-background group focus-within:ring-2 ring-primary/20 transition-all">
            <Search className="w-5 h-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
            <Input 
              placeholder="Ex: Encanador, Eletricista..." 
              className="border-none shadow-none focus-visible:ring-0 bg-transparent h-14 text-base font-semibold"
            />
          </div>
        </section>

        {/* Quick Actions */}
        <section className="grid grid-cols-1 gap-4">
          <Button variant="neo-elevated" className="h-20 rounded-2xl flex justify-between items-center px-6 group">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl neo-inset bg-primary/10 flex items-center justify-center">
                <Plus className="w-6 h-6 text-primary" />
              </div>
              <div className="text-left">
                <span className="block font-bold text-lg">Criar Novo Pedido</span>
                <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground opacity-60">Gratuito e rápido</span>
              </div>
            </div>
            <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:translate-x-1 transition-transform" />
          </Button>
        </section>

        {/* Active Requests */}
        <section className="space-y-4">
          <div className="flex justify-between items-center px-1">
            <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/80">Seus Pedidos Ativos</h3>
            <Button variant="link" size="sm" className="text-xs font-bold text-primary px-0">Ver todos</Button>
          </div>

          <div className="space-y-4">
            {activeRequests.map((req) => (
              <Card key={req.id} variant="neo-elevated" className="border-none rounded-[2rem] p-2 hover:translate-y-[-2px] transition-transform cursor-pointer group">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg font-bold">{req.title}</CardTitle>
                    <span className="text-[10px] font-mono font-bold px-3 py-1 bg-primary/20 text-primary rounded-full uppercase">
                      {req.status}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4 text-xs font-medium text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {req.date}
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" /> São Paulo, SP
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>

      {/* Suggestion Grid */}
      <section className="px-6 mt-12 max-w-2xl mx-auto">
        <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/80 px-1 mb-4">Categorias Populares</h3>
        <div className="grid grid-cols-2 gap-4">
          {["Limpeza", "Reformas", "Elétrica", "Pintura"].map((cat) => (
            <Button key={cat} variant="neo-elevated" className="h-16 rounded-2xl bg-background font-bold text-sm">
              {cat}
            </Button>
          ))}
        </div>
      </section>
    </main>
  )
}
