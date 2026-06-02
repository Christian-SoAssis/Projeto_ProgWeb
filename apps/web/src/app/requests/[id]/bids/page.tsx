"use client"

import { useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import {
    ChevronLeft,
    Star,
    DollarSign,
    Clock,
    MessageSquare,
    CheckCircle,
    XCircle,
    Inbox,
} from "lucide-react"
import { useBids } from "@/hooks/useBids"
import { bidRepository } from "@/repositories"
import { Contract } from "@/domain/models/contract"
import { formatCurrency } from "@/lib/formatters"
import { apiFetch } from "@/lib/api"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"

function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    })
}

const STATUS_LABEL: Record<string, { label: string; color: string }> = {
    pending: { label: "Aguardando", color: "text-yellow-600" },
    accepted: { label: "Aceito", color: "text-green-600" },
    rejected: { label: "Recusado", color: "text-destructive" },
    cancelled: { label: "Cancelado", color: "text-muted-foreground" },
}

export default function BidsPage() {
    const params = useParams()
    const router = useRouter()
    const requestId = params.id as string
    const { bids, loading, reload } = useBids(requestId)
    const [processing, setProcessing] = useState<string | null>(null)
    const [acceptedContract, setAcceptedContract] = useState<Contract | null>(null)

    // Scheduling States
    const [isScheduling, setIsScheduling] = useState(false)
    const [selectedBidId, setSelectedBidId] = useState<string | null>(null)
    const [selectedProId, setSelectedProId] = useState<string | null>(null)
    const [scheduledDate, setScheduledDate] = useState(() => {
        const tomorrow = new Date()
        tomorrow.setDate(tomorrow.getDate() + 1)
        return tomorrow.toISOString().split("T")[0]
    })
    const [availableSlots, setAvailableSlots] = useState<{ start_time: string; end_time: string }[]>([])
    const [selectedSlot, setSelectedSlot] = useState<string | null>(null)
    const [loadingSlots, setLoadingSlots] = useState(false)

    async function loadSlots(dateStr: string, proId: string) {
        setLoadingSlots(true)
        try {
            const data = await apiFetch(`/professionals/${proId}/available-slots?date=${dateStr}`)
            setAvailableSlots(data || [])
            setSelectedSlot(null)
        } catch (err) {
            toast.error("Erro ao buscar horários disponíveis.")
        } finally {
            setLoadingSlots(false)
        }
    }

    async function handleAcceptClick(bidId: string, proId: string) {
        setSelectedBidId(bidId)
        setSelectedProId(proId)
        setIsScheduling(true)
        
        const tomorrow = new Date()
        tomorrow.setDate(tomorrow.getDate() + 1)
        const tomorrowStr = tomorrow.toISOString().split("T")[0]
        setScheduledDate(tomorrowStr)
        await loadSlots(tomorrowStr, proId)
    }

    async function confirmAccept() {
        if (!selectedBidId || !selectedSlot) {
            toast.error("Por favor, selecione um horário.")
            return
        }
        setProcessing(selectedBidId)
        setIsScheduling(false)
        try {
            const scheduledStart = new Date(`${scheduledDate}T${selectedSlot}:00`).toISOString()
            const { bid, contract } = await bidRepository.updateStatus(selectedBidId, "accepted", scheduledStart)
            if (contract) setAcceptedContract(contract)
            toast.success("Lance aceito e serviço agendado com sucesso!", {
                description: "Contrato criado com sucesso.",
            })
            reload()
        } catch (err: any) {
            toast.error("Erro ao aceitar lance", { description: err.message })
        } finally {
            setProcessing(null)
            setSelectedBidId(null)
            setSelectedProId(null)
            setSelectedSlot(null)
        }
    }

    async function handleReject(bidId: string) {
        setProcessing(bidId)
        try {
            await bidRepository.updateStatus(bidId, "rejected")
            toast.success("Lance recusado.")
            reload()
        } catch (err: any) {
            toast.error("Erro ao recusar lance", { description: err.message })
        } finally {
            setProcessing(null)
        }
    }

    return (
        <main className="min-h-screen bg-background pb-20 px-6 max-w-lg mx-auto">
            <div className="pt-6 pb-2">
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => router.push("/dashboard/client")}
                    className="gap-2 text-muted-foreground"
                >
                    <ChevronLeft className="w-4 h-4" /> Dashboard
                </Button>
            </div>

            <div className="mb-6">
                <h1 className="text-2xl font-extrabold tracking-tight">
                    Lances <span className="text-primary italic">Recebidos</span>
                </h1>
                <p className="text-sm text-muted-foreground mt-1 font-medium">
                    Aceite um lance para fechar o contrato.
                </p>
            </div>

            {acceptedContract && (
                <Card variant="neo-elevated" className="border-none rounded-[2rem] p-5 mb-6 bg-green-50 dark:bg-green-950">
                    <div className="flex items-center gap-3 mb-3">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <span className="font-bold text-green-700 dark:text-green-400">Contrato Criado!</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                        Valor acordado:{" "}
                        <span className="font-bold text-foreground">
                            {formatCurrency(acceptedContract.agreedCents)}
                        </span>
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                        Contrato ID: <span className="font-mono">{acceptedContract.id.slice(0, 8)}…</span>
                    </p>
                    <Button
                        variant="neo-elevated"
                        size="sm"
                        className="mt-3 h-8 text-xs font-bold text-primary"
                        onClick={() =>
                            router.push(
                                `/reviews/new?contractId=${acceptedContract.id}`
                            )
                        }
                    >
                        Deixar Avaliação
                    </Button>
                </Card>
            )}

            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <Card key={i} variant="neo-elevated" className="border-none rounded-[2rem] p-5">
                            <Skeleton className="h-4 w-24 mb-3" />
                            <Skeleton className="h-6 w-32 mb-2" />
                            <Skeleton className="h-3 w-48" />
                        </Card>
                    ))}
                </div>
            ) : bids.length === 0 ? (
                <Card
                    variant="neo-elevated"
                    className="border-none rounded-[2rem] p-8 text-center flex flex-col items-center gap-4"
                >
                    <div className="w-16 h-16 neo-inset rounded-3xl flex items-center justify-center bg-background/50">
                        <Inbox className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <div>
                        <h3 className="font-bold text-lg">Nenhum lance recebido</h3>
                        <p className="text-sm text-muted-foreground mt-1">
                            Os profissionais ainda não enviaram propostas.
                        </p>
                    </div>
                </Card>
            ) : (
                <div className="space-y-4">
                    {bids.map((bid) => {
                        const statusInfo = STATUS_LABEL[bid.status] ?? { label: bid.status, color: "" }
                        const isPending = bid.status === "pending"
                        const isLoading = processing === bid.id

                        return (
                            <Card
                                key={bid.id}
                                variant="neo-elevated"
                                className="border-none rounded-[2rem] p-5 space-y-3"
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex items-center gap-2 text-primary">
                                        <DollarSign className="w-4 h-4" />
                                        <span className="text-xl font-black">
                                            {formatCurrency(bid.priceCents)}
                                        </span>
                                    </div>
                                    <span className={`text-xs font-bold uppercase tracking-wider ${statusInfo.color}`}>
                                        {statusInfo.label}
                                    </span>
                                </div>

                                <div className="flex flex-wrap gap-4 text-xs font-medium text-muted-foreground">
                                    {bid.estimatedHours && (
                                        <div className="flex items-center gap-1">
                                            <Clock className="w-3 h-3 text-primary" />
                                            {bid.estimatedHours}h estimadas
                                        </div>
                                    )}
                                    <div className="flex items-center gap-1">
                                        <Star className="w-3 h-3 text-primary" />
                                        {formatDate(bid.createdAt)}
                                    </div>
                                </div>

                                {bid.message && (
                                    <div className="neo-inset rounded-xl p-3 flex gap-2">
                                        <MessageSquare className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                                        <p className="text-xs text-muted-foreground leading-relaxed">
                                            {bid.message}
                                        </p>
                                    </div>
                                )}

                                {isPending && (
                                    <div className="flex gap-2 pt-1 border-t border-muted/20">
                                        <Button
                                            variant="neo-elevated"
                                            className="flex-1 h-9 rounded-xl text-xs font-bold text-green-600 gap-1"
                                            onClick={() => handleAcceptClick(bid.id, bid.professionalId)}
                                            disabled={isLoading}
                                        >
                                            <CheckCircle className="w-3.5 h-3.5" />
                                            {isLoading ? "Processando…" : "Aceitar"}
                                        </Button>
                                        <Button
                                            variant="neo-elevated"
                                            className="flex-1 h-9 rounded-xl text-xs font-bold text-destructive gap-1"
                                            onClick={() => handleReject(bid.id)}
                                            disabled={isLoading}
                                        >
                                            <XCircle className="w-3.5 h-3.5" />
                                            {isLoading ? "Processando…" : "Recusar"}
                                        </Button>
                                    </div>
                                )}
                            </Card>
                        )
                    })}
                </div>
            )}
            <Dialog open={isScheduling} onOpenChange={setIsScheduling}>
                <DialogContent className="bg-background border-none rounded-[2rem] p-6 neo-elevated max-w-sm">
                    <DialogHeader>
                        <DialogTitle className="font-extrabold text-lg text-left">Agendar Atendimento</DialogTitle>
                        <DialogDescription className="text-xs text-muted-foreground text-left">
                            Escolha a data e um horário disponível do profissional para realizar o serviço.
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4 my-3 text-left">
                        <div className="space-y-1.5">
                            <label className="text-[10px] font-black uppercase tracking-wider text-muted-foreground">
                                Data do Serviço
                            </label>
                            <input
                                type="date"
                                value={scheduledDate}
                                min={new Date().toISOString().split("T")[0]}
                                onChange={(e) => {
                                    setScheduledDate(e.target.value)
                                    if (selectedProId) loadSlots(e.target.value, selectedProId)
                                }}
                                className="w-full h-12 px-4 rounded-xl bg-background border-none text-xs font-bold neo-inset focus:outline-none"
                            />
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-[10px] font-black uppercase tracking-wider text-muted-foreground">
                                Horários Disponíveis
                            </label>
                            
                            {loadingSlots ? (
                                <div className="grid grid-cols-3 gap-2">
                                    {[1, 2, 3].map(i => (
                                        <div key={i} className="h-9 bg-muted/20 animate-pulse rounded-lg" />
                                    ))}
                                </div>
                            ) : availableSlots.length === 0 ? (
                                <div className="p-3 bg-muted/10 rounded-xl text-center">
                                    <p className="text-[10px] font-bold text-muted-foreground">
                                        Nenhum horário disponível para esta data. Tente outro dia.
                                    </p>
                                </div>
                            ) : (
                                <div className="grid grid-cols-3 gap-2 max-h-40 overflow-y-auto pr-1">
                                    {availableSlots.map((slot) => {
                                        const isSelected = selectedSlot === slot.start_time
                                        return (
                                            <button
                                                key={slot.start_time}
                                                type="button"
                                                onClick={() => setSelectedSlot(slot.start_time)}
                                                className={`
                                                    h-9 rounded-lg text-xs font-bold transition-all
                                                    ${isSelected 
                                                        ? "neo-inset text-primary ring-2 ring-primary/20" 
                                                        : "neo-elevated hover:translate-y-[-1px] text-muted-foreground"
                                                    }
                                                `}
                                            >
                                                {slot.start_time}
                                            </button>
                                        )
                                    })}
                                </div>
                            )}
                        </div>
                    </div>

                    <DialogFooter className="flex gap-2 pt-2 border-t border-muted/20">
                        <Button
                            variant="neo-elevated"
                            className="flex-1 h-12 rounded-xl text-xs font-bold text-muted-foreground"
                            onClick={() => setIsScheduling(false)}
                        >
                            Cancelar
                        </Button>
                        <Button
                            variant="neo-elevated"
                            disabled={!selectedSlot}
                            className="flex-1 h-12 rounded-xl text-xs font-bold text-primary"
                            onClick={confirmAccept}
                        >
                            Confirmar
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </main>
    )
}
