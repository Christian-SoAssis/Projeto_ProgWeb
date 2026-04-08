"use client"

import { NotificationBell } from "./NotificationBell"
import { User, LogOut, ChevronDown } from "lucide-react"
import { useState } from "react"
import { useAuth } from "@/context/auth-context"

interface DashboardHeaderProps {
  userName: string
  roleLabel: string
}

export function DashboardHeader({ userName, roleLabel }: DashboardHeaderProps) {
  const [profileOpen, setProfileOpen] = useState(false)
  const { logout } = useAuth()

  return (
    <header className="w-full flex justify-between items-center px-6 py-4 mb-2">
      <div className="flex flex-col">
        <h2 className="text-xl font-extrabold tracking-tight">
          Serviço<span className="text-primary italic">Já</span>
        </h2>
        <span className="text-[9px] font-mono font-bold uppercase tracking-widest text-muted-foreground opacity-60">
          {roleLabel} Dashboard
        </span>
      </div>

      <div className="flex items-center gap-4">
        <NotificationBell hasNotifications={true} />
        
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className={`
              flex items-center gap-3 p-2 pr-4 rounded-2xl transition-all duration-300
              ${profileOpen ? "neo-inset" : "neo-elevated hover:bg-muted/5"}
            `}
          >
            <div className="w-10 h-10 rounded-xl neo-inset flex items-center justify-center bg-background/50">
              <User className="w-5 h-5 text-primary" />
            </div>
            <div className="hidden sm:flex flex-col items-start leading-tight">
              <span className="text-sm font-bold truncate max-w-[100px]">{userName}</span>
              <span className="text-[10px] text-muted-foreground font-medium lowercase">Perfil</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform duration-300 ${profileOpen ? "rotate-180" : ""}`} />
          </button>

          {profileOpen && (
            <div className="absolute right-0 mt-3 w-48 py-2 bg-background rounded-2xl neo-elevated border-none z-50 animate-in fade-in slide-in-from-top-2 duration-200">
              <button className="w-full px-4 py-2 text-left text-sm font-medium hover:text-primary transition-colors flex items-center gap-2">
                <User className="w-4 h-4" /> Meu Perfil
              </button>
              <div className="h-px bg-muted/20 my-1 mx-2" />
              <button 
                onClick={logout}
                className="w-full px-4 py-2 text-left text-sm font-bold text-destructive hover:bg-destructive/5 transition-colors flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" /> Sair
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
