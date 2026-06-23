"use client"

import { DashboardHeader } from "@/components/dashboard/DashboardHeader"
import { useAuth } from "@/presentation/hooks/use-auth"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { User, Mail, Calendar, Settings, LogOut, ChevronLeft } from "lucide-react"
import Link from "next/link"

export default function ClientProfile() {
  const { user, logout } = useAuth()

  return (
    <main className="min-h-screen bg-background pb-20">
      <DashboardHeader userName={user?.name || "Cliente"} roleLabel="Cliente" />

      <div className="px-6 space-y-8 max-w-2xl mx-auto mt-6">
        <section>
          <div className="flex items-center gap-3 mb-4">
            <Link 
              href="/dashboard/client"
              className="w-10 h-10 rounded-full neo-elevated hover:bg-muted/5 flex items-center justify-center transition-all shrink-0"
            >
              <ChevronLeft className="w-5 h-5 text-muted-foreground" />
            </Link>
            <h2 className="text-xl font-black">Meu Perfil</h2>
          </div>
          <Card variant="neo-elevated" className="border-none rounded-3xl p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-full neo-inset flex items-center justify-center bg-background/50">
                <User className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h3 className="font-bold text-lg">{user?.name}</h3>
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <Mail className="w-3 h-3" /> {user?.email}
                </p>
              </div>
            </div>
            
            <div className="space-y-3 border-t border-muted/20 pt-4">
               <div className="flex justify-between items-center text-sm">
                 <span className="font-medium text-muted-foreground flex items-center gap-2">
                   <Calendar className="w-4 h-4" /> Membro desde
                 </span>
                 <span className="font-bold">2026</span>
               </div>
            </div>
          </Card>
        </section>

        <section className="space-y-4">
          <Button variant="neo-elevated" className="w-full h-14 rounded-2xl justify-start px-6" asChild>
            <Link href="/profile/client/settings">
              <Settings className="w-5 h-5 mr-3 text-primary" />
              <span className="font-bold">Configurações da Conta</span>
            </Link>
          </Button>
          <Button 
            variant="neo-elevated" 
            className="w-full h-14 rounded-2xl justify-start px-6 text-destructive hover:text-destructive"
            onClick={() => logout()}
          >
            <LogOut className="w-5 h-5 mr-3" />
            <span className="font-bold">Sair da Conta</span>
          </Button>
        </section>
      </div>
    </main>
  )
}
