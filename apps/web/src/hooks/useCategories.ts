import { useState, useEffect } from "react"
import { categoriesService } from "@/services/categories.service"
import type { Category } from "@/types/category"

export function useCategories() {
    const [categories, setCategories] = useState<Category[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        categoriesService.list()
            .then(setCategories)
            .catch(() => setError("Erro ao carregar categorias"))
            .finally(() => setLoading(false))
    }, [])

    return { categories, loading, error }
}
