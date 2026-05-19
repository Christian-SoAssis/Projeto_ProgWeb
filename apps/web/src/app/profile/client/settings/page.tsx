"use client"

import React, { useState } from "react"
import { useRouter } from "next/navigation"
import { 
  ChevronLeft, 
  Sun, 
  Moon, 
  Bell, 
  User, 
  Globe, 
  MapPin, 
  Trash2, 
  LogOut,
  Laptop,
  Check
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useAuth } from "@/context/auth-context"
import { toast } from "sonner"

type ThemeMode = "claro" | "escuro" | "sistema"

export default function SettingsAppearancePage() {
  const router = useRouter()
  const { user, logout } = useAuth()

  // Estados locais para as preferências
  const [selectedTheme, setSelectedTheme] = useState<ThemeMode>("claro")
  const [syncWithSystem, setSyncWithSystem] = useState(false)
  const [notifyBids, setNotifyBids] = useState(true)
  const [notifyChat, setNotifyChat] = useState(true)
  const [notifyContracts, setNotifyContracts] = useState(false)

  // Handlers para ações rápidas de conta
  const handleClearCache = () => {
    toast.success("Cache limpo com sucesso!", {
      description: "24.8 MB de arquivos temporários foram removidos.",
      className: "neo-elevated rounded-2xl border-none text-foreground font-bold"
    })
  }

  const handleLanguageChange = () => {
    toast.info("Idioma selecionado: Português (BR)", {
      className: "neo-elevated rounded-2xl border-none text-foreground font-bold"
    })
  }

  const handleRegionChange = () => {
    toast.info("Região selecionada: Brasil", {
      className: "neo-elevated rounded-2xl border-none text-foreground font-bold"
    })
  }

  return (
    <main className="min-h-screen bg-background flex justify-center items-start sm:py-6 relative font-sans">
      
      {/* Container Frame Mobile-First */}
      <div className="w-full max-w-[480px] bg-background min-h-screen sm:min-h-[840px] sm:rounded-[2.5rem] sm:neo-elevated overflow-hidden flex flex-col relative border-none pb-12">
        
        {/* HEADER NEOMÓRFICO */}
        <header className="px-5 py-4 bg-background neo-elevated flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => router.push("/profile/client")}
              className="w-10 h-10 rounded-full neo-elevated hover:bg-muted/5 flex items-center justify-center transition-all"
            >
              <ChevronLeft className="w-5 h-5 text-muted-foreground" />
            </button>
            <h2 className="text-base font-black text-foreground/90">Aparência e Ajustes</h2>
          </div>
          <div className="w-10 h-10 rounded-full neo-inset flex items-center justify-center text-primary">
            <User className="w-5 h-5" />
          </div>
        </header>

        {/* ÁREA DE CONFIGURAÇÕES */}
        <div className="flex-1 px-5 py-5 space-y-6 overflow-y-auto">

          {/* SEÇÃO 1: APARÊNCIA */}
          <section className="space-y-3.5">
            <h3 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/80 px-1">
              Personalização Visual
            </h3>
            
            <Card className="border-none rounded-[2rem] p-5 space-y-5 neo-elevated">
              
              {/* Theme Segmented Control */}
              <div className="space-y-2.5">
                <label className="text-[11px] font-black uppercase tracking-wider text-muted-foreground">
                  Tema do Aplicativo
                </label>
                
                {/* Track Oval Afundado */}
                <div className="h-14 rounded-2xl neo-inset bg-background/50 flex p-1.5 items-center justify-between relative">
                  
                  {/* Opção Claro */}
                  <button 
                    type="button"
                    onClick={() => setSelectedTheme("claro")}
                    className={`
                      flex-1 h-full rounded-[10px] flex items-center justify-center gap-2 text-xs font-bold transition-all duration-300
                      ${selectedTheme === "claro" 
                        ? "bg-background text-[#1a9878] neo-elevated shadow-neo-elevated font-extrabold" 
                        : "text-muted-foreground hover:text-foreground"
                      }
                    `}
                  >
                    <Sun className="w-4 h-4" />
                    <span>Claro</span>
                  </button>

                  {/* Opção Escuro */}
                  <button 
                    type="button"
                    onClick={() => setSelectedTheme("escuro")}
                    className={`
                      flex-1 h-full rounded-[10px] flex items-center justify-center gap-2 text-xs font-bold transition-all duration-300
                      ${selectedTheme === "escuro" 
                        ? "bg-background text-[#1a9878] neo-elevated shadow-neo-elevated font-extrabold" 
                        : "text-muted-foreground hover:text-foreground"
                      }
                    `}
                  >
                    <Moon className="w-4 h-4" />
                    <span>Escuro</span>
                  </button>

                  {/* Opção Sistema */}
                  <button 
                    type="button"
                    onClick={() => setSelectedTheme("sistema")}
                    className={`
                      flex-1 h-full rounded-[10px] flex items-center justify-center gap-2 text-xs font-bold transition-all duration-300
                      ${selectedTheme === "sistema" 
                        ? "bg-background text-[#1a9878] neo-elevated shadow-neo-elevated font-extrabold" 
                        : "text-muted-foreground hover:text-foreground"
                      }
                    `}
                  >
                    <Laptop className="w-4 h-4" />
                    <span>Sistema</span>
                  </button>

                </div>
              </div>

              {/* Dynamic Live Preview Card */}
              <div className="space-y-2.5">
                <label className="text-[11px] font-black uppercase tracking-wider text-muted-foreground">
                  Pré-visualização da Interface
                </label>
                
                {/* O mini-card simula a interface em tempo real */}
                <div 
                  className={`
                    w-full h-32 rounded-2xl p-4 flex flex-col justify-between transition-all duration-500 relative overflow-hidden border-none
                    ${selectedTheme === "escuro" 
                      ? "bg-[#25222e] text-slate-100 shadow-[inset_-3px_-3px_7px_#342f40,inset_3px_3px_7px_#16151c]" 
                      : "bg-background text-foreground neo-inset"
                    }
                  `}
                >
                  {/* Mini Header */}
                  <div className="flex justify-between items-center w-full">
                    <div className="flex flex-col">
                      <span className="text-[9px] font-black leading-none">ServiçoJá</span>
                      <span className="text-[6px] font-bold text-muted-foreground uppercase mt-0.5">Preview</span>
                    </div>
                    <div className={`w-4.5 h-4.5 rounded-full ${selectedTheme === "escuro" ? "bg-[#342f40] shadow-[-1px_-1px_3px_#474057,1px_1px_3px_#16151c]" : "neo-elevated"} flex items-center justify-center`}>
                      <span className="w-1.5 h-1.5 rounded-full bg-[#1a9878]" />
                    </div>
                  </div>

                  {/* Mini Cards Row */}
                  <div className="grid grid-cols-2 gap-3 my-1">
                    <div className={`p-2 rounded-lg text-left ${selectedTheme === "escuro" ? "bg-[#25222e] shadow-[-2px_-2px_5px_#342f40,2px_2px_5px_#16151c]" : "neo-elevated"}`}>
                      <div className="w-3 h-3 rounded bg-primary/20" />
                      <div className="w-8 h-1 bg-muted-foreground/30 rounded mt-1.5" />
                    </div>
                    <div className={`p-2 rounded-lg text-left ${selectedTheme === "escuro" ? "bg-[#25222e] shadow-[-2px_-2px_5px_#342f40,2px_2px_5px_#16151c]" : "neo-elevated"}`}>
                      <div className="w-3 h-3 rounded bg-secondary/30" />
                      <div className="w-10 h-1 bg-muted-foreground/30 rounded mt-1.5" />
                    </div>
                  </div>

                  {/* Mini Status */}
                  <div className="w-full flex justify-between items-center text-[7px] font-bold text-muted-foreground">
                    <span>Modo {selectedTheme.charAt(0).toUpperCase() + selectedTheme.slice(1)}</span>
                    <span className="font-mono text-[#1a9878]">R$ 270,00</span>
                  </div>
                </div>
              </div>

              {/* Sync with Device Toggle */}
              <div className="flex items-center justify-between pt-1">
                <div className="flex flex-col text-left">
                  <span className="text-xs font-bold text-foreground">Sincronizar com o dispositivo</span>
                  <span className="text-[10px] text-muted-foreground font-medium">Ajusta o tema conforme as configurações do sistema.</span>
                </div>
                
                {/* Custom Neomorphic Toggle Switch */}
                <button 
                  type="button"
                  onClick={() => {
                    setSyncWithSystem(!syncWithSystem)
                    if(!syncWithSystem) {
                      setSelectedTheme("sistema")
                    } else {
                      setSelectedTheme("claro")
                    }
                  }}
                  className={`
                    w-12 h-6 rounded-full p-0.5 transition-all duration-300 focus:outline-none relative shrink-0
                    ${syncWithSystem ? "neo-inset bg-background" : "neo-inset"}
                  `}
                >
                  <div 
                    className={`
                      w-5 h-5 rounded-full transition-all duration-300 flex items-center justify-center
                      ${syncWithSystem 
                        ? "translate-x-6 bg-[#1a9878] shadow-[0_0_10px_rgba(26,152,120,.5)] text-primary-foreground" 
                        : "translate-x-0 bg-background neo-elevated text-muted-foreground"
                      }
                    `}
                  >
                    {syncWithSystem && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                  </div>
                </button>
              </div>

            </Card>
          </section>

          {/* SEÇÃO 2: NOTIFICAÇÕES */}
          <section className="space-y-3.5">
            <h3 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/80 px-1">
              Preferências de Alerta
            </h3>
            
            <Card className="border-none rounded-[2rem] p-5 space-y-4 neo-elevated">
              
              {/* Row 1: Novos lances */}
              <div className="flex items-center justify-between">
                <div className="flex flex-col text-left">
                  <span className="text-xs font-bold text-foreground">Novos lances recebidos</span>
                  <span className="text-[10px] text-muted-foreground font-medium">Alertar sobre novas propostas em pedidos.</span>
                </div>
                
                <button 
                  type="button"
                  onClick={() => setNotifyBids(!notifyBids)}
                  className="w-12 h-6 rounded-full p-0.5 neo-inset focus:outline-none shrink-0"
                >
                  <div 
                    className={`
                      w-5 h-5 rounded-full transition-all duration-300 flex items-center justify-center
                      ${notifyBids 
                        ? "translate-x-6 bg-[#1a9878] shadow-[0_0_10px_rgba(26,152,120,.5)] text-primary-foreground" 
                        : "translate-x-0 bg-background neo-elevated text-muted-foreground"
                      }
                    `}
                  >
                    {notifyBids && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                  </div>
                </button>
              </div>

              <div className="h-px bg-muted/20 my-0.5" />

              {/* Row 2: Mensagens chat */}
              <div className="flex items-center justify-between">
                <div className="flex flex-col text-left">
                  <span className="text-xs font-bold text-foreground">Mensagens no chat</span>
                  <span className="text-[10px] text-muted-foreground font-medium">Notificações de conversas em tempo real.</span>
                </div>
                
                <button 
                  type="button"
                  onClick={() => setNotifyChat(!notifyChat)}
                  className="w-12 h-6 rounded-full p-0.5 neo-inset focus:outline-none shrink-0"
                >
                  <div 
                    className={`
                      w-5 h-5 rounded-full transition-all duration-300 flex items-center justify-center
                      ${notifyChat 
                        ? "translate-x-6 bg-[#1a9878] shadow-[0_0_10px_rgba(26,152,120,.5)] text-primary-foreground" 
                        : "translate-x-0 bg-background neo-elevated text-muted-foreground"
                      }
                    `}
                  >
                    {notifyChat && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                  </div>
                </button>
              </div>

              <div className="h-px bg-muted/20 my-0.5" />

              {/* Row 3: Atualizações de contrato */}
              <div className="flex items-center justify-between">
                <div className="flex flex-col text-left">
                  <span className="text-xs font-bold text-foreground">Atualizações de contrato</span>
                  <span className="text-[10px] text-muted-foreground font-medium">Mudanças de status e progresso do serviço.</span>
                </div>
                
                <button 
                  type="button"
                  onClick={() => setNotifyContracts(!notifyContracts)}
                  className="w-12 h-6 rounded-full p-0.5 neo-inset focus:outline-none shrink-0"
                >
                  <div 
                    className={`
                      w-5 h-5 rounded-full transition-all duration-300 flex items-center justify-center
                      ${notifyContracts 
                        ? "translate-x-6 bg-[#1a9878] shadow-[0_0_10px_rgba(26,152,120,.5)] text-primary-foreground" 
                        : "translate-x-0 bg-background neo-elevated text-muted-foreground"
                      }
                    `}
                  >
                    {notifyContracts && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                  </div>
                </button>
              </div>

            </Card>
          </section>

          {/* SEÇÃO 3: AJUSTES DA CONTA */}
          <section className="space-y-3.5">
            <h3 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/80 px-1">
              Ajustes do Sistema
            </h3>
            
            <Card className="border-none rounded-[2rem] p-5 space-y-4 neo-elevated">
              
              {/* Row Idioma */}
              <button 
                onClick={handleLanguageChange}
                className="w-full flex items-center justify-between hover:bg-muted/5 p-2 rounded-xl transition-all"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl neo-inset flex items-center justify-center bg-background/50 text-primary">
                    <Globe className="w-4 h-4" />
                  </div>
                  <div className="flex flex-col text-left">
                    <span className="text-xs font-bold text-foreground">Idioma</span>
                    <span className="text-[10px] text-muted-foreground font-medium">Português (BR)</span>
                  </div>
                </div>
                <div className="w-6 h-6 rounded-full neo-elevated flex items-center justify-center font-bold text-xs text-muted-foreground">
                  ›
                </div>
              </button>

              <div className="h-px bg-muted/20" />

              {/* Row Região */}
              <button 
                onClick={handleRegionChange}
                className="w-full flex items-center justify-between hover:bg-muted/5 p-2 rounded-xl transition-all"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl neo-inset flex items-center justify-center bg-background/50 text-primary">
                    <MapPin className="w-4 h-4" />
                  </div>
                  <div className="flex flex-col text-left">
                    <span className="text-xs font-bold text-foreground">Região</span>
                    <span className="text-[10px] text-muted-foreground font-medium">Brasil</span>
                  </div>
                </div>
                <div className="w-6 h-6 rounded-full neo-elevated flex items-center justify-center font-bold text-xs text-muted-foreground">
                  ›
                </div>
              </button>

              <div className="h-px bg-muted/20" />

              {/* Row Limpar Cache */}
              <button 
                onClick={handleClearCache}
                className="w-full flex items-center justify-between hover:bg-muted/5 p-2 rounded-xl transition-all"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-9 h-9 rounded-xl neo-inset flex items-center justify-center bg-background/50 text-primary">
                    <Trash2 className="w-4 h-4" />
                  </div>
                  <div className="flex flex-col text-left">
                    <span className="text-xs font-bold text-foreground">Limpar cache</span>
                    <span className="text-[10px] text-muted-foreground font-medium">Libera 24.8 MB de arquivos de visualização.</span>
                  </div>
                </div>
                <div className="w-6 h-6 rounded-full neo-elevated flex items-center justify-center font-bold text-xs text-muted-foreground">
                  ›
                </div>
              </button>

            </Card>
          </section>

          {/* BOTÃO DE SAÍDA (LOGOUT DESTRUTIVO GHOST) */}
          <div className="pt-2 text-center">
            <Button
              variant="ghost"
              onClick={() => logout()}
              className="w-full h-14 bg-background text-[#b04020] font-black text-sm rounded-xl neo-elevated hover:bg-muted/5 transition-all flex items-center justify-center gap-2 border-none shadow-none"
            >
              <LogOut className="w-4.5 h-4.5" />
              Sair da Conta
            </Button>
          </div>

        </div>

      </div>
    </main>
  )
}
