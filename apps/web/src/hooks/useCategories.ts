import { useState, useEffect } from "react"
import { categoryRepository } from "@/repositories"
import type { Category } from "@/domain/models/category"

export function useCategories() {
    const [categories, setCategories] = useState<Category[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        categoryRepository.list()
            .then(setCategories)
            .catch(() => setError("Erro ao carregar categorias"))
            .finally(() => setLoading(false))
    }, [])

    return { categories, loading, error }
}
