import { UserEntity } from "../../domain/entities/user.entity";
import { AuthTokensVo } from "../../domain/value-objects/auth-tokens.vo";
import { LoginDto } from "../dto/login.dto";
import { RegisterClientDto } from "../dto/register-client.dto";

export interface AuthRepositoryPort {
  login(dto: LoginDto): Promise<AuthTokensVo>;
  registerClient(dto: RegisterClientDto): Promise<AuthTokensVo>;
  getCurrentUser(): Promise<UserEntity>;
  switchRole(): Promise<AuthTokensVo>;
}
