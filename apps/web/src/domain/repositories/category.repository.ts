import { Category } from "../models/category";

export interface CategoryRepository {
    list(): Promise<Category[]>;
}
