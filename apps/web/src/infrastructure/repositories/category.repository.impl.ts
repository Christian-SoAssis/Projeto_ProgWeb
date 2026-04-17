import { apiFetch } from "@/lib/api";
import { Category } from "../../domain/models/category";
import { CategoryRepository } from "../../domain/repositories/category.repository";

export class CategoryRepositoryImpl implements CategoryRepository {
    async list(): Promise<Category[]> {
        return apiFetch("/categories");
    }
}
