import { Contract } from "../models/contract";

export interface ContractRepository {
    getById(id: string): Promise<Contract>;
}
