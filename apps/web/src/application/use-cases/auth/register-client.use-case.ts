import { UserEntity } from "../../../domain/entities/user.entity";
import { RegisterClientDto } from "../../dto/register-client.dto";
import { AuthRepositoryPort } from "../../ports/auth-repository.port";
import { TokenStoragePort } from "../../ports/token-storage.port";

export class RegisterClientUseCase {
  constructor(
    private readonly authRepository: AuthRepositoryPort,
    private readonly tokenStorage: TokenStoragePort
  ) {}

  public async execute(dto: RegisterClientDto): Promise<UserEntity> {
    const tokens = await this.authRepository.registerClient(dto);
    this.tokenStorage.saveTokens(tokens);
    const user = await this.authRepository.getCurrentUser();
    return user;
  }
}
