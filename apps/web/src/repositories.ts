import { BidRepositoryImpl } from "./infrastructure/repositories/bid.repository.impl";
import { RequestRepositoryImpl } from "./infrastructure/repositories/request.repository.impl";
import { ProfessionalRepositoryImpl } from "./infrastructure/repositories/professional.repository.impl";
import { CategoryRepositoryImpl } from "./infrastructure/repositories/category.repository.impl";

// Singletons or Factory methods
export const bidRepository = new BidRepositoryImpl();
export const requestRepository = new RequestRepositoryImpl();
export const professionalRepository = new ProfessionalRepositoryImpl();
export const categoryRepository = new CategoryRepositoryImpl();
