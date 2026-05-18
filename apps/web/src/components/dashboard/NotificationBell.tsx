"use client"

import { Bell, CheckCheck, DollarSign, Star, FileCheck, X } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { useNotifications } from "@/hooks/useNotifications"
import { Notification } from "@/domain/models/notification"

const TYPE_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
    new_bid: {
        label: "Novo Lance",
        icon: <DollarSign className="w-4 h-4" />,
        color: "text-primary",
    },
    bid_accepted: {
        label: "Lance Aceito",
        icon: <CheckCheck className="w-4 h-4" />,
        color: "text-green-600",
    },
    bid_rejected: {
        label: "Lance Recusado",
        icon: <X className="w-4 h-4" />,
        color: "text-destructive",
    },
    new_review: {
        label: "Nova Avaliação",
        icon: <Star className="w-4 h-4" />,
        color: "text-yellow-500",
    },
    contract_completed: {
        label: "Serviço Concluído",
        icon: <FileCheck className="w-4 h-4" />,
        color: "text-green-600",
    },
}

function formatRelative(iso: string) {
    const diff = Date.now() - new Date(iso).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return "agora"
    if (mins < 60) return `${mins}min atrás`
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return `${hrs}h atrás`
    return `${Math.floor(hrs / 24)}d atrás`
}

function getDescription(n: Notification): string {
    const p = n.payload
    switch (n.type) {
        case "new_bid":
            return p.message || `Lance de R$ ${((p.price_cents ?? 0) / 100).toFixed(2)}`
        case "bid_accepted":
            return "Seu lance foi aceito! Contrato criado."
        case "bid_rejected":
            return "Seu lance foi recusado pelo cliente."
        case "new_review":
            return p.text ? p.text.slice(0, 60) + "…" : "Você recebeu uma nova avaliação."
        case "contract_completed":
            return "Um contrato foi marcado como concluído."
        default:
            return p.message || n.type
    }
}

export function NotificationBell() {
    const [open, setOpen] = useState(false)
    const ref = useRef<HTMLDivElement>(null)
    const { notifications, unreadCount, loading, markRead } = useNotifications()

    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (ref.current && !ref.current.contains(e.target as Node)) {
                setOpen(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [])

    function handleOpen() {
        setOpen((v) => !v)
        if (!open) {
            const unreadIds = notifications
                .filter((n) => n.readAt === null)
                .map((n) => n.id)
            if (unreadIds.length > 0) markRead(unreadIds)
        }
    }

    return (
        <div className="relative" ref={ref}>
            <button
                onClick={handleOpen}
                className={`
                    relative w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-200
                    ${open
                        ? "neo-inset text-primary scale-95"
                        : "neo-elevated text-muted-foreground hover:text-primary active:scale-90"
                    }
                `}
            >
                <Bell className={`w-5 h-5 ${open ? "fill-primary/20" : ""}`} />

                {unreadCount > 0 && !open && (
                    <span className="absolute top-2.5 right-2.5 min-w-[16px] h-4 bg-primary rounded-full ring-2 ring-background flex items-center justify-center">
                        <span className="text-[9px] font-black text-primary-foreground px-0.5">
                            {unreadCount > 9 ? "9+" : unreadCount}
                        </span>
                    </span>
                )}
            </button>

            {open && (
                <div className="absolute right-0 mt-3 w-80 bg-background rounded-2xl neo-elevated border-none z-50 animate-in fade-in slide-in-from-top-2 duration-200 overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-3 border-b border-muted/20">
                        <span className="text-sm font-bold">Notificações</span>
                        {notifications.length > 0 && (
                            <span className="text-[10px] font-mono text-muted-foreground">
                                {notifications.length} total
                            </span>
                        )}
                    </div>

                    <div className="max-h-80 overflow-y-auto">
                        {loading ? (
                            <div className="p-6 text-center text-sm text-muted-foreground">
                                Carregando…
                            </div>
                        ) : notifications.length === 0 ? (
                            <div className="p-6 text-center flex flex-col items-center gap-2">
                                <Bell className="w-8 h-8 text-muted-foreground/40" />
                                <p className="text-sm text-muted-foreground">
                                    Nenhuma notificação ainda.
                                </p>
                            </div>
                        ) : (
                            notifications.map((n) => {
                                const config = TYPE_CONFIG[n.type]
                                const isUnread = n.readAt === null
                                return (
                                    <div
                                        key={n.id}
                                        className={`flex gap-3 px-4 py-3 border-b border-muted/10 transition-colors ${
                                            isUnread ? "bg-primary/5" : ""
                                        }`}
                                    >
                                        <div
                                            className={`w-8 h-8 rounded-xl neo-inset flex items-center justify-center shrink-0 ${
                                                config?.color ?? "text-muted-foreground"
                                            }`}
                                        >
                                            {config?.icon ?? <Bell className="w-4 h-4" />}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center justify-between gap-2">
                                                <span className="text-xs font-bold truncate">
                                                    {config?.label ?? n.type}
                                                </span>
                                                <span className="text-[10px] text-muted-foreground shrink-0">
                                                    {formatRelative(n.createdAt)}
                                                </span>
                                            </div>
                                            <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                                                {getDescription(n)}
                                            </p>
                                        </div>
                                        {isUnread && (
                                            <div className="w-1.5 h-1.5 rounded-full bg-primary shrink-0 mt-1.5" />
                                        )}
                                    </div>
                                )
                            })
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
