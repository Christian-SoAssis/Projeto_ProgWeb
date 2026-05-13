"use client"

import { useState } from "react"
import { toast } from "sonner"
import { Bid } from "@/domain/models/bid"
import { CreateBidPayload } from "@/domain/repositories/bid.repository"
import { bidRepository } from "@/repositories"

export function useCreateBid() {
    const [isSubmitting, setIsSubmitting] = useState(false)

    async function createBid(payload: CreateBidPayload): Promise<Bid> {
        setIsSubmitting(true)
        try {
            const bid = await bidRepository.create(payload)
            toast.success("Lance enviado!", {
                description: "Aguarde a resposta do cliente.",
            })
            return bid
        } catch (err: any) {
            toast.error("Erro ao enviar lance", { description: err.message })
            throw err
        } finally {
            setIsSubmitting(false)
        }
    }

    return { createBid, isSubmitting }
}
