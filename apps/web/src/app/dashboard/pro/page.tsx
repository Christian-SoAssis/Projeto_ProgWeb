"use client"

import { useState } from "react"
import { DashboardHeader } from "@/components/dashboard/DashboardHeader"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { MapPin, Star, DollarSign, Briefcase, Zap, AlertCircle, Clock, X, BadgeCheck, User as UserIcon } from "lucide-react"
import { useAuth } from "@/presentation/hooks/use-auth"
import { useProfessionalMetrics } from "@/hooks/useProfessionalMetrics"
import { useProfessionalProfile } from "@/hooks/useProfessionalProfile"
import { useGeolocation } from "@/hooks/useGeolocation"
import { useAvailableRequests } from "@/hooks/useAvailableRequests"
import { useCreateBid } from "@/hooks/useCreateBid"
import { formatCurrency } from "@/lib/formatters"
import { ServiceRequest } from "@/domain/models/request"

const URGENCY_LABEL: Record<string, string> = {
    immediate: "Urgente",
    scheduled: "Agendado",
    flexible: "Flexível",
}

function BidModal({
    request,
    onClose,
}: {
    request: ServiceRequest
    onClose: () => void
}) {
    const { createBid, isSubmitting } = useCreateBid()
    const [price, setPrice] = useState("")
    const [hours, setHours] = useState("")
    const [message, setMessage] = useState("")

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        const priceCents = Math.round(parseFloat(price.replace(",", ".")) * 100)
        if (!priceCents || priceCents <= 0) return

        try {
            await createBid({
                requestId: request.id,
                priceCents,
                estimatedHours: hours ? parseInt(hours) : undefined,
                message: message.trim() || undefined,
            })
            onClose()
        } catch {
            // toast já exibido pelo hook
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 backdrop-blur-sm px-4">
            <Card
                variant="neo-elevated"
                className="w-full max-w-md border-none rounded-[2rem] p-6 space-y-5"
            >
                <div className="flex justify-between items-start">
                    <div>
                        <h2 className="font-extrabold text-lg">Enviar Lance</h2>
                        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                            {request.title}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-1.5">
                        <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                            Valor (R$) *
                        </label>
                        <input
                            type="number"
                            min="1"
                            step="0.01"
                            placeholder="Ex: 250,00"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            required
                            className="w-full neo-inset rounded-xl px-4 py-2.5 text-sm bg-background focus:outline-none"
                        />
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                            Horas estimadas
                        </label>
                        <input
                            type="number"
                            min="1"
                            placeholder="Ex: 3"
                            value={hours}
                            onChange={(e) => setHours(e.target.value)}
                            className="w-full neo-inset rounded-xl px-4 py-2.5 text-sm bg-background focus:outline-none"
                        />
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                            Mensagem (opcional)
                        </label>
                        <textarea
                            rows={3}
                            maxLength={500}
                            placeholder="Descreva brevemente sua proposta…"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            className="w-full neo-inset rounded-xl px-4 py-2.5 text-sm bg-background focus:outline-none resize-none"
                        />
                    </div>

                    <Button
                        type="submit"
                        variant="neo-elevated"
                        className="w-full h-11 rounded-xl font-bold text-primary"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? "Enviando…" : "Confirmar Lance"}
                    </Button>
                </form>
            </Card>
        </div>
    )
}

export default function ProfessionalDashboard() {
    const { user } = useAuth()
    const { metrics, loading: loadingMetrics } = useProfessionalMetrics()
    const { profile, loading: loadingProfile } = useProfessionalProfile()
    const { isLocating, error: locationError } = useGeolocation()
    const { requests, loading: loadingRequests } = useAvailableRequests()
    const [selectedRequest, setSelectedRequest] = useState<ServiceRequest | null>(null)

    const openRequests = requests.filter((r) => r.status === "open")

    return (
        <main className="min-h-screen bg-background pb-20">
            <DashboardHeader userName={user?.name || "Profissional"} roleLabel="Profissional" />

            {selectedRequest && (
                <BidModal
                    request={selectedRequest}
                    onClose={() => setSelectedRequest(null)}
                />
            )}

            <div className="px-6 mt-6 space-y-8 max-w-2xl mx-auto">
                {/* PROFILE CARD */}
                <Card variant="neo-elevated" className="border-none rounded-[2rem] p-6 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-bl-[100px] -z-10" />
                    <div className="flex items-start gap-5">
                        <div className="w-20 h-20 shrink-0 rounded-[1.5rem] neo-inset flex items-center justify-center bg-background overflow-hidden">
                            {user?.avatarUrl ? (
                                <img src={user.avatarUrl} alt="Avatar" className="w-full h-full object-cover" />
                            ) : (
                                <UserIcon className="w-8 h-8 text-muted-foreground/50" />
                            )}
                        </div>
                        <div className="flex-1 space-y-1 pt-1">
                            <div className="flex items-center gap-2">
                                <h2 className="text-xl font-black leading-none">{user?.name || "..."}</h2>
                                {profile?.is_verified && (
                                    <BadgeCheck className="w-5 h-5 text-primary" />
                                )}
                            </div>
                            <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                                {profile?.categories?.map(c => c.name).join(" • ") || "Profissional"}
                            </p>
                            
                            <div className="pt-2">
                                {loadingProfile ? (
                                    <Skeleton className="h-4 w-full" />
                                ) : (
                                    <p className="text-sm text-foreground/80 line-clamp-3 leading-relaxed">
                                        {profile?.bio || "Sua biografia aparecerá aqui..."}
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                </Card>

                {/* EXECUTIVE METRICS GRID */}
                <section className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <Card variant="neo-elevated" className="border-none rounded-3xl p-5 flex flex-col justify-between min-h-[110px]">
                        <div className="flex justify-between items-start">
                            <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground opacity-70">
                                Avaliação
                            </span>
                            <Star className="w-4 h-4 text-primary fill-primary/20" />
                        </div>
                        <div className="mt-2">
                            {loadingMetrics ? <Skeleton className="h-8 w-16" /> : (
                                <span className="text-3xl font-black text-primary">
                                    {metrics?.reputationScore?.toFixed(1) ?? "—"}
                                </span>
                            )}
                        </div>
                    </Card>

                    <Card variant="neo-elevated" className="border-none rounded-3xl p-5 flex flex-col justify-between min-h-[110px]">
                        <div className="flex justify-between items-start">
                            <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground opacity-70">
                                Ganhos
                            </span>
                            <DollarSign className="w-4 h-4 text-secondary" />
                        </div>
                        <div className="mt-2">
                            {loadingMetrics ? <Skeleton className="h-8 w-24" /> : (
                                <span className="text-xl sm:text-2xl font-black truncate text-secondary">
                                    {metrics ? formatCurrency(metrics.totalEarningsCents) : "—"}
                                </span>
                            )}
                        </div>
                    </Card>
                    
                    <Card variant="neo-elevated" className="border-none rounded-3xl p-5 flex flex-col justify-between min-h-[110px] col-span-2 md:col-span-1">
                        <div className="flex justify-between items-start">
                            <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground opacity-70">
                                Concluídos
                            </span>
                            <Briefcase className="w-4 h-4 text-foreground/50" />
                        </div>
                        <div className="mt-2">
                            {loadingMetrics ? <Skeleton className="h-8 w-12" /> : (
                                <span className="text-3xl font-black text-foreground">
                                    {metrics?.completedJobs ?? "0"}
                                </span>
                            )}
                        </div>
                    </Card>
                </section>

                {(locationError || isLocating) && (
                    <section>
                        <div
                            className={`neo-inset rounded-2xl p-4 flex items-center gap-3 ${locationError ? "text-destructive" : "text-primary"}`}
                        >
                            {isLocating ? (
                                <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                            ) : (
                                <AlertCircle className="w-5 h-5" />
                            )}
                            <span className="text-xs font-bold">
                                {isLocating
                                    ? "Obtendo sua localização para filtrar serviços próximos..."
                                    : locationError}
                            </span>
                        </div>
                    </section>
                )}

                <section className="space-y-4">
                    <div className="flex justify-between items-center px-1">
                        <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground/80 flex items-center gap-2">
                            <Zap className="w-4 h-4 text-primary fill-primary/20" /> Oportunidades Próximas
                        </h3>
                        <span className="text-xs font-bold text-muted-foreground">
                            {openRequests.length} abertas
                        </span>
                    </div>

                    {loadingRequests ? (
                        <div className="space-y-4">
                            {[1, 2, 3].map((i) => (
                                <Card key={i} variant="neo-elevated" className="border-none rounded-[2rem] p-4">
                                    <Skeleton className="h-5 w-48 mb-2" />
                                    <Skeleton className="h-3 w-32 mb-3" />
                                    <Skeleton className="h-8 w-full rounded-xl" />
                                </Card>
                            ))}
                        </div>
                    ) : openRequests.length === 0 ? (
                        <Card
                            variant="neo-elevated"
                            className="border-none rounded-[2rem] p-6 text-center text-sm text-muted-foreground"
                        >
                            Nenhuma oportunidade disponível no momento.
                        </Card>
                    ) : (
                        <div className="space-y-4">
                            {openRequests.map((req) => (
                                <Card
                                    key={req.id}
                                    variant="neo-elevated"
                                    className="border-none rounded-[2rem] p-4 hover:translate-y-[-2px] transition-transform cursor-pointer group"
                                >
                                    <div className="flex justify-between items-start mb-3">
                                        <div className="flex-1 min-w-0 pr-2">
                                            <h4 className="text-base font-bold group-hover:text-primary transition-colors line-clamp-1">
                                                {req.title}
                                            </h4>
                                            {req.description && (
                                                <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
                                                    {req.description}
                                                </p>
                                            )}
                                        </div>
                                        {req.budgetCents && (
                                            <div className="bg-background neo-inset px-3 py-2 rounded-xl text-xs font-black text-secondary shrink-0">
                                                {formatCurrency(req.budgetCents)}
                                            </div>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-4 border-t border-muted/20 pt-3">
                                        <div className="flex items-center gap-1 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                                            <MapPin className="w-3 h-3 text-primary" />
                                            {req.latitude.toFixed(2)}, {req.longitude.toFixed(2)}
                                        </div>
                                        <div className="flex items-center gap-1 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                                            <Clock className="w-3 h-3 text-primary" />
                                            {URGENCY_LABEL[req.urgency] ?? req.urgency}
                                        </div>
                                        <Button
                                            variant="neo-elevated"
                                            size="sm"
                                            className="ml-auto h-8 px-4 rounded-xl text-[10px] font-bold text-primary shadow-none"
                                            onClick={() => setSelectedRequest(req)}
                                        >
                                            Dar Lance
                                        </Button>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    )}
                </section>

                <section>
                    <div className="neo-elevated rounded-3xl p-6 bg-primary/5 flex gap-4 items-center">
                        <div className="w-12 h-12 rounded-2xl neo-inset flex items-center justify-center bg-background/50">
                            <Zap className="w-6 h-6 text-primary animate-pulse" />
                        </div>
                        <div className="flex-1">
                            <h5 className="font-bold text-sm">Aumente sua visibilidade</h5>
                            <p className="text-xs text-muted-foreground">
                                Torne-se um profissional verificado para ganhar preferência nos lances.
                            </p>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    )
}
