import { RegisterProfessionalDto } from "../../dto/register-professional.dto";
import { ProfessionalRepositoryPort } from "../../ports/professional-repository.port";
import { AuthRepositoryPort } from "../../ports/auth-repository.port";
import { TokenStoragePort } from "../../ports/token-storage.port";
import { UserEntity } from "../../../domain/entities/user.entity";

export class RegisterProfessionalUseCase {
  constructor(
    private readonly professionalRepository: ProfessionalRepositoryPort,
    private readonly authRepository: AuthRepositoryPort,
    private readonly tokenStorage: TokenStoragePort
  ) {}

  /**
   * Executa o caso de uso de registro de profissionais.
   * Como o backend de criação não retorna tokens diretamente, tentamos realizar
   * o auto-login logo em seguida para melhorar a experiência do usuário.
   * Se o auto-login falhar (por exemplo, se o perfil necessitar de aprovação prévia),
   * retornamos { requiresManualLogin: true } para que a UI redirecione para o fluxo de login.
   */
  public async execute(
    dto: RegisterProfessionalDto
  ): Promise<{ user: UserEntity; autoLoggedIn: true } | { requiresManualLogin: true }> {
    // 1. Envia a requisição de cadastro do profissional à infraestrutura
    await this.professionalRepository.register(dto);

    try {
      // 2. Tenta efetuar o login automático utilizando as credenciais recém-criadas
      const tokens = await this.authRepository.login({
        email: dto.email,
        password: dto.password,
      });

      // 3. Persiste os tokens e carrega o perfil do usuário recém-logado
      this.tokenStorage.saveTokens(tokens);
      const user = await this.authRepository.getCurrentUser();
      
      return { user, autoLoggedIn: true };
    } catch (error) {
      // Fallback em caso de falha de login (ex: necessidade de verificação administrativa)
      console.warn("Auto-login falhou pós-registro. Redirecionando para login manual.", error);
      return { requiresManualLogin: true };
    }
  }
}
