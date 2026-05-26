import { AuthRepositoryPort } from "../../application/ports/auth-repository.port";
import { LoginDto } from "../../application/dto/login.dto";
import { RegisterClientDto } from "../../application/dto/register-client.dto";
import { UserEntity } from "../../domain/entities/user.entity";
import { AuthTokensVo } from "../../domain/value-objects/auth-tokens.vo";
import { HttpClient } from "../http/http-client";
import { RawUserDto, UserMapper } from "../mappers/user.mapper";
import { HttpError } from "../http/http.error";
import { InvalidCredentialsError } from "../../domain/errors/invalid-credentials.error";
import { DomainError } from "../../domain/errors/domain.error";

interface RawLoginResponse {
  access_token: string;
  refresh_token: string;
}

export class HttpAuthRepository implements AuthRepositoryPort {
  constructor(private readonly httpClient: HttpClient) {}

  public async login(dto: LoginDto): Promise<AuthTokensVo> {
    try {
      const response = await this.httpClient.post<RawLoginResponse>("/auth/login", dto);
      return new AuthTokensVo(response.access_token, response.refresh_token);
    } catch (error) {
      if (error instanceof HttpError && (error.status === 401 || error.status === 403)) {
        throw new InvalidCredentialsError("E-mail ou senha incorretos");
      }
      throw new DomainError(error instanceof Error ? error.message : "Falha ao realizar login");
    }
  }

  public async registerClient(dto: RegisterClientDto): Promise<AuthTokensVo> {
    try {
      const payload = {
        name: dto.name,
        email: dto.email,
        phone: dto.phone,
        password: dto.password,
        consent_terms: dto.consentTerms,
        consent_privacy: dto.consentPrivacy,
      };

      const response = await this.httpClient.post<RawLoginResponse>("/auth/register", payload);
      return new AuthTokensVo(response.access_token, response.refresh_token);
    } catch (error) {
      throw new DomainError(
        error instanceof Error ? error.message : "Falha ao registrar cliente"
      );
    }
  }

  public async getCurrentUser(): Promise<UserEntity> {
    try {
      const response = await this.httpClient.get<RawUserDto>("/auth/me");
      return UserMapper.toDomain(response);
    } catch (error) {
      throw new DomainError(
        error instanceof Error ? error.message : "Falha ao obter perfil do usuário logado"
      );
    }
  }

  public async switchRole(): Promise<AuthTokensVo> {
    try {
      const response = await this.httpClient.post<RawLoginResponse>("/auth/test/switch-role");
      return new AuthTokensVo(response.access_token, response.refresh_token);
    } catch (error) {
      throw new DomainError(
        error instanceof Error ? error.message : "Falha ao alternar perfil de acesso"
      );
    }
  }
}
