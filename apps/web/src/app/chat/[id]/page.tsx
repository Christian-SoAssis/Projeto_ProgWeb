"use client"

import React, { useState, useEffect, useRef } from "react"
import { useParams, useRouter } from "next/navigation"
import { 
  ChevronLeft, 
  Info, 
  Phone, 
  Camera, 
  Paperclip, 
  Send, 
  CheckCheck, 
  X,
  FileText,
  DollarSign,
  Calendar,
  Wrench
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface Message {
  id: string
  sender: "client" | "professional"
  text: string
  timestamp: string
  status: "sent" | "delivered" | "read"
}

export default function SecureChatPage() {
  const params = useParams()
  const router = useRouter()
  const chatUrlId = params.id as string
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Estados locais
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "professional",
      text: "Olá! Acabei de chegar no local e já estou com as ferramentas prontas. Vou começar o reparo do vazamento da pia agora.",
      timestamp: "17:15",
      status: "read"
    },
    {
      id: "2",
      sender: "client",
      text: "Perfeito, Marcos! O registro geral fica na área de serviço externa, caso precise fechar a água.",
      timestamp: "17:18",
      status: "read"
    },
    {
      id: "3",
      sender: "professional",
      text: "Encontrei aqui, obrigado. O cano antigo de PVC estava trincado mesmo. Vou fazer a substituição pelo tubo de alta resistência.",
      timestamp: "17:22",
      status: "read"
    }
  ])
  const [inputText, setInputText] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [isContractModalOpen, setIsContractModalOpen] = useState(false)

  // Scroll automático para a última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isTyping])

  // Função para simular respostas automáticas inteligentes
  const simulateProfessionalReply = (clientText: string) => {
    setIsTyping(true)
    
    // Tempo aleatório realista de digitação
    setTimeout(() => {
      setIsTyping(false)
      
      let replyText = ""
      const textLower = clientText.toLowerCase()
      
      if (textLower.includes("obrigado") || textLower.includes("valeu") || textLower.includes("show")) {
        replyText = "Disponha! O serviço ficou excelente e testei várias vezes sob pressão."
      } else if (textLower.includes("quanto") || textLower.includes("preço") || textLower.includes("valor")) {
        replyText = "O valor total já está fechado no contrato por R$ 270,00, sem nenhuma taxa adicional."
      } else if (textLower.includes("terminou") || textLower.includes("acabou") || textLower.includes("pronto")) {
        replyText = "Sim! Finalizei todas as vedações e limpei o local. Tudo 100% resolvido."
      } else {
        replyText = "Entendido. Vou focar em finalizar essa parte e já te aviso se precisar de algo."
      }

      const now = new Date()
      const timestamp = now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })
      
      setMessages(prev => [
        ...prev,
        {
          id: String(prev.length + 1),
          sender: "professional",
          text: replyText,
          timestamp,
          status: "read"
        }
      ])
    }, 2000)
  }

  // Ação de envio de mensagem
  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim()) return

    const now = new Date()
    const timestamp = now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })
    
    const userMessage: Message = {
      id: String(messages.length + 1),
      sender: "client",
      text: inputText.trim(),
      timestamp,
      status: "sent"
    }

    setMessages(prev => [...prev, userMessage])
    const sentText = inputText
    setInputText("")

    // Simula confirmação de recebimento (WebSocket)
    setTimeout(() => {
      setMessages(prev => 
        prev.map(m => m.id === userMessage.id ? { ...m, status: "read" } : m)
      )
      // Simula resposta do profissional
      simulateProfessionalReply(sentText)
    }, 800)
  }

  return (
    <main className="min-h-screen bg-background flex justify-center items-start sm:py-6 relative font-sans">
      
      {/* Container Frame Mobile-First */}
      <div className="w-full max-w-[480px] bg-background min-h-screen sm:min-h-[840px] sm:rounded-[2.5rem] sm:neo-elevated overflow-hidden flex flex-col relative border-none">
        
        {/* HEADER NEOMÓRFICO */}
        <header className="px-5 py-4 bg-background neo-elevated flex items-center justify-between z-10 shrink-0">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => router.push("/dashboard/client")}
              className="w-10 h-10 rounded-full neo-elevated hover:bg-muted/5 flex items-center justify-center transition-all"
            >
              <ChevronLeft className="w-5 h-5 text-muted-foreground" />
            </button>
            
            {/* Avatar & Info */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-11 h-11 rounded-full neo-inset flex items-center justify-center bg-background p-0.5 overflow-hidden">
                  <img 
                    src="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&auto=format&fit=crop&q=80" 
                    alt="Marcos Silva" 
                    className="w-full h-full object-cover rounded-full"
                  />
                </div>
                {/* Pulsating status dot */}
                <span className="absolute bottom-0 right-0 w-3 h-3 bg-[#1a9878] border-2 border-background rounded-full">
                  <span className="absolute inset-0 bg-[#1a9878] rounded-full animate-ping opacity-75" />
                </span>
              </div>
              
              <div className="flex flex-col">
                <h3 className="text-sm font-black leading-tight text-foreground/90">Marcos Silva</h3>
                <span className="text-[10px] font-bold text-[#006951] uppercase tracking-wider">
                  Hidráulica
                </span>
              </div>
            </div>
          </div>

          {/* Action Icons */}
          <div className="flex gap-2">
            <button className="w-9 h-9 rounded-xl neo-elevated hover:bg-muted/5 flex items-center justify-center transition-all">
              <Phone className="w-4 h-4 text-muted-foreground" />
            </button>
            <button className="w-9 h-9 rounded-xl neo-elevated hover:bg-muted/5 flex items-center justify-center transition-all">
              <Info className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
        </header>

        {/* BANNER DE CONTRATO ATIVO */}
        <section className="px-5 pt-3 pb-3 bg-background z-10 shrink-0">
          <Card className="border-none rounded-2xl neo-elevated p-3 relative overflow-hidden">
            {/* Accent menta top border */}
            <div className="absolute top-0 left-0 right-0 h-[3px] bg-[#1a9878]" />
            
            <div className="flex items-center justify-between mt-0.5">
              <div className="space-y-0.5">
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] font-black uppercase tracking-widest text-[#1a9878]">
                    Contrato Ativo
                  </span>
                  <span className="w-1.5 h-1.5 rounded-full bg-yellow-500 animate-pulse" />
                </div>
                <h4 className="text-xs font-bold text-muted-foreground">
                  Reparo Hidráulico Residencial
                </h4>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-sm font-black font-mono text-foreground tracking-tight">
                  R$ 270,00
                </span>
                <button 
                  onClick={() => setIsContractModalOpen(true)}
                  className="px-3 py-1.5 rounded-xl neo-inset hover:bg-muted/5 text-[10px] font-black text-primary uppercase tracking-wider transition-all"
                >
                  Ver contrato
                </button>
              </div>
            </div>
          </Card>
        </section>

        {/* ÁREA DE CONVERSA */}
        <section className="flex-1 bg-[#c4c0d0] neo-inset overflow-y-auto px-5 py-4 space-y-4 flex flex-col scrollbar-thin">
          {messages.map((msg) => {
            const isMe = msg.sender === "client"
            return (
              <div 
                key={msg.id}
                className={`flex w-full ${isMe ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2 duration-300`}
              >
                <div className="max-w-[75%] flex flex-col gap-1">
                  
                  {/* Bolha Neomórfica */}
                  <div 
                    className={`
                      px-4 py-3 text-sm leading-relaxed
                      ${isMe 
                        ? "bg-background text-foreground neo-elevated rounded-[16px_4px_16px_16px] bg-gradient-to-br from-background to-[rgba(26,152,120,.05)]" 
                        : "bg-[#c4c0d0] text-foreground/90 neo-inset rounded-[4px_16px_16px_16px]"
                      }
                    `}
                  >
                    <p className="whitespace-pre-line font-medium">{msg.text}</p>
                  </div>

                  {/* Timestamp & Status Icon */}
                  <div className={`flex items-center gap-1.5 text-[9px] font-bold text-muted-foreground/80 mt-0.5 ${isMe ? "justify-end" : "justify-start"}`}>
                    <span>{msg.timestamp}</span>
                    {isMe && (
                      <CheckCheck className={`w-3.5 h-3.5 ${msg.status === "read" ? "text-primary" : "text-muted-foreground/50"}`} />
                    )}
                  </div>

                </div>
              </div>
            )
          })}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex w-full justify-start animate-in fade-in duration-300">
              <div className="flex flex-col gap-1">
                <div className="px-4 py-3 bg-[#c4c0d0] neo-inset rounded-[4px_16px_16px_16px] flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-1.5 h-1.5 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-1.5 h-1.5 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <span className="text-[9px] font-bold text-muted-foreground/80">
                  Marcos Silva está digitando...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </section>

        {/* BARRA DE ENTRADA DE TEXTO (INPUT) */}
        <section className="p-4 bg-background z-10 shrink-0">
          <form onSubmit={handleSendMessage} className="flex items-center gap-3">
            
            {/* Input Oval Afundado */}
            <div className="flex-1 h-12 rounded-full neo-inset bg-background flex items-center px-4 gap-2">
              <button 
                type="button"
                className="w-8 h-8 rounded-full neo-elevated hover:bg-muted/5 flex items-center justify-center text-muted-foreground shrink-0 transition-all"
              >
                <Camera className="w-4 h-4" />
              </button>
              <button 
                type="button"
                className="w-8 h-8 rounded-full neo-elevated hover:bg-muted/5 flex items-center justify-center text-muted-foreground shrink-0 transition-all"
              >
                <Paperclip className="w-4 h-4" />
              </button>
              
              <input
                type="text"
                placeholder="Conversar de forma segura..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="flex-1 bg-transparent border-none text-sm font-semibold outline-none focus:ring-0 text-foreground"
              />
            </div>

            {/* Botão Enviar Circular */}
            <button 
              type="submit"
              disabled={!inputText.trim()}
              className={`
                w-12 h-12 rounded-full flex items-center justify-center shrink-0 transition-all duration-300
                ${inputText.trim() 
                  ? "bg-primary text-primary-foreground neo-elevated hover:scale-105 active:scale-95" 
                  : "bg-muted text-muted-foreground cursor-not-allowed opacity-60 neo-inset"
                }
              `}
            >
              <Send className="w-4.5 h-4.5" />
            </button>
          </form>

          {/* BOTÃO CTA DE CONCLUSÃO DE SERVIÇO */}
          <div className="mt-3.5 pt-0.5">
            <Button
              onClick={() => router.push(`/reviews/new?contractId=${chatUrlId}`)}
              className="w-full h-12 bg-primary text-primary-foreground font-black text-sm rounded-xl neo-elevated hover:bg-primary/95 transition-all flex items-center justify-center gap-1 shadow-none border-none"
            >
              Confirmar conclusão e avaliar →
            </Button>
          </div>
        </section>

        {/* MODAL DETALHADO DO CONTRATO */}
        {isContractModalOpen && (
          <div className="absolute inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center px-4 z-50 animate-in fade-in duration-200">
            <Card className="w-full max-w-sm border-none rounded-[2rem] p-6 space-y-6 neo-elevated relative animate-in zoom-in-95 duration-200">
              
              {/* Close Button */}
              <button 
                onClick={() => setIsContractModalOpen(false)}
                className="absolute top-4 right-4 w-8 h-8 rounded-full neo-elevated hover:bg-muted/5 flex items-center justify-center transition-all"
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </button>

              <div className="text-center">
                <h3 className="text-base font-black text-foreground">Detalhes do Contrato</h3>
                <p className="text-xs text-muted-foreground mt-1">Serviço em andamento seguro</p>
              </div>

              {/* Detalhes do Contrato */}
              <div className="space-y-3 pt-2">
                
                <div className="flex items-center gap-3 p-3 rounded-xl neo-inset bg-background/50">
                  <Wrench className="w-5 h-5 text-primary" />
                  <div className="text-left">
                    <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">Serviço</span>
                    <span className="text-xs font-bold text-foreground">Reparo Hidráulico Residencial</span>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 rounded-xl neo-inset bg-background/50">
                  <DollarSign className="w-5 h-5 text-primary" />
                  <div className="text-left">
                    <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">Valor Total</span>
                    <span className="text-xs font-mono font-black text-foreground">R$ 270,00</span>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 rounded-xl neo-inset bg-background/50">
                  <Calendar className="w-5 h-5 text-primary" />
                  <div className="text-left">
                    <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">Data de Início</span>
                    <span className="text-xs font-bold text-foreground">Hoje, às 17:10</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl neo-inset bg-background/50 text-left">
                  <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block mb-1">Escopo Acordado</span>
                  <p className="text-[11px] font-medium text-foreground/80 leading-relaxed">
                    Substituição de cano trincado de PVC por tubo de alta resistência sob a pia e testes de vedação sob pressão de água para garantir a contenção completa do vazamento.
                  </p>
                </div>

              </div>

              {/* Botão de Fechar */}
              <Button
                onClick={() => setIsContractModalOpen(false)}
                className="w-full h-11 bg-background text-primary font-bold text-sm rounded-xl neo-elevated hover:bg-muted/5 transition-all shadow-none border-none"
              >
                Fechar Detalhes
              </Button>

            </Card>
          </div>
        )}

      </div>
    </main>
  )
}
