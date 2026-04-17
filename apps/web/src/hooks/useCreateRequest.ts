import { useState } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { requestRepository } from "@/repositories"
import type { CreateRequestPayload } from "@/domain/repositories/request.repository"

export function useCreateRequest() {
    const router = useRouter()
    const [isSubmitting, setIsSubmitting] = useState(false)

    async function createRequest(payload: CreateRequestPayload) {
        setIsSubmitting(true)
        try {
            const data = await requestRepository.create(payload)
            toast.success("Pedido criado!", {
                description: "Buscando profissionais próximos...",
            })
            router.push(`/requests/${data.id}/matches`)
        } catch (err: any) {
            toast.error("Erro ao criar pedido", { description: err.message })
        } finally {
            setIsSubmitting(false)
        }
    }

    return { createRequest, isSubmitting }
}
