import { RegisterProfessionalDto } from "../dto/register-professional.dto";

export interface ProfessionalRepositoryPort {
  register(dto: RegisterProfessionalDto): Promise<void>;
}
