import { UserEntity } from "../../../domain/entities/user.entity";
import { LoginDto } from "../../dto/login.dto";
import { AuthRepositoryPort } from "../../ports/auth-repository.port";
import { TokenStoragePort } from "../../ports/token-storage.port";

export class LoginUseCase {
  constructor(
    private readonly authRepository: AuthRepositoryPort,
    private readonly tokenStorage: TokenStoragePort
  ) {}

  public async execute(dto: LoginDto): Promise<UserEntity> {
    const tokens = await this.authRepository.login(dto);
    this.tokenStorage.saveTokens(tokens);
    const user = await this.authRepository.getCurrentUser();
    return user;
  }
}
