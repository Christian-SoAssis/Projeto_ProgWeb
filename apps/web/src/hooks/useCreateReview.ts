"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { CreateReviewPayload } from "@/domain/repositories/review.repository"
import { reviewRepository } from "@/repositories"

export function useCreateReview() {
    const router = useRouter()
    const [isSubmitting, setIsSubmitting] = useState(false)

    async function createReview(payload: CreateReviewPayload) {
        setIsSubmitting(true)
        try {
            await reviewRepository.create(payload)
            toast.success("Avaliação enviada!", {
                description: "Obrigado pelo seu feedback.",
            })
            router.push("/dashboard/client")
        } catch (err: any) {
            toast.error("Erro ao enviar avaliação", { description: err.message })
        } finally {
            setIsSubmitting(false)
        }
    }

    return { createReview, isSubmitting }
}
