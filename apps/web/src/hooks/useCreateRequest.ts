import { useState } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { requestsService } from "@/services/requests.service"
import type { CreateRequestPayload } from "@/types/request"

export function useCreateRequest() {
    const router = useRouter()
    const [isSubmitting, setIsSubmitting] = useState(false)

    async function createRequest(payload: CreateRequestPayload) {
        setIsSubmitting(true)
        try {
            const data = await requestsService.create(payload)
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
