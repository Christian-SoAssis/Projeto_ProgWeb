"use client"

import { useState, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ChevronLeft, Star } from "lucide-react"
import { useCreateReview } from "@/hooks/useCreateReview"

function StarRating({
    value,
    onChange,
}: {
    value: number
    onChange: (v: number) => void
}) {
    const [hovered, setHovered] = useState(0)

    return (
        <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    type="button"
                    onClick={() => onChange(star)}
                    onMouseEnter={() => setHovered(star)}
                    onMouseLeave={() => setHovered(0)}
                    className="transition-transform hover:scale-110"
                >
                    <Star
                        className={`w-8 h-8 transition-colors ${
                            star <= (hovered || value)
                                ? "fill-primary text-primary"
                                : "text-muted-foreground"
                        }`}
                    />
                </button>
            ))}
        </div>
    )
}

function ReviewForm() {
    const searchParams = useSearchParams()
    const router = useRouter()
    const contractId = searchParams.get("contractId") ?? ""
    const { createReview, isSubmitting } = useCreateReview()

    const [rating, setRating] = useState(0)
    const [text, setText] = useState("")

    const canSubmit = rating > 0 && text.trim().length >= 10 && contractId

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        if (!canSubmit) return
        await createReview({ contractId, rating, text: text.trim() })
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
                    Avaliar <span className="text-primary italic">Serviço</span>
                </h1>
                <p className="text-sm text-muted-foreground mt-1 font-medium">
                    Sua avaliação ajuda outros clientes e o profissional a melhorar.
                </p>
            </div>

            {!contractId ? (
                <Card
                    variant="neo-elevated"
                    className="border-none rounded-[2rem] p-8 text-center text-sm text-muted-foreground"
                >
                    Contrato não identificado. Acesse esta página pelo link de aceite de lance.
                </Card>
            ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                    <Card variant="neo-elevated" className="border-none rounded-[2rem] p-6 space-y-5">
                        <div className="space-y-3">
                            <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                                Nota geral *
                            </label>
                            <StarRating value={rating} onChange={setRating} />
                            {rating > 0 && (
                                <p className="text-xs text-muted-foreground">
                                    {
                                        ["", "Muito ruim", "Ruim", "Regular", "Bom", "Excelente"][
                                            rating
                                        ]
                                    }
                                </p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                                Comentário *{" "}
                                <span className="normal-case font-normal tracking-normal">
                                    (mínimo 10 caracteres)
                                </span>
                            </label>
                            <textarea
                                rows={5}
                                maxLength={2000}
                                placeholder="Conte como foi a experiência com o profissional…"
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                required
                                className="w-full neo-inset rounded-xl px-4 py-3 text-sm bg-background focus:outline-none resize-none"
                            />
                            <p className="text-[10px] text-muted-foreground text-right">
                                {text.length}/2000
                            </p>
                        </div>
                    </Card>

                    <Button
                        type="submit"
                        variant="neo-elevated"
                        className="w-full h-12 rounded-2xl font-bold text-primary text-sm"
                        disabled={!canSubmit || isSubmitting}
                    >
                        {isSubmitting ? "Enviando…" : "Enviar Avaliação"}
                    </Button>
                </form>
            )}
        </main>
    )
}

export default function ReviewPage() {
    return (
        <Suspense>
            <ReviewForm />
        </Suspense>
    )
}
