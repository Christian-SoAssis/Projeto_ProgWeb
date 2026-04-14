import { apiFetch } from "@/lib/api"
import type { Category } from "@/types/category"

export const categoriesService = {
    async list(): Promise<Category[]> {
        return apiFetch("/categories")
    },
}
