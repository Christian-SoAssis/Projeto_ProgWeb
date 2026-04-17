import { BidRepositoryImpl } from "./infrastructure/repositories/bid.repository.impl";
import { RequestRepositoryImpl } from "./infrastructure/repositories/request.repository.impl";

// Singletons or Factory methods
export const bidRepository = new BidRepositoryImpl();
export const requestRepository = new RequestRepositoryImpl();
