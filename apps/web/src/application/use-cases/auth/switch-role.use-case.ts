import { UserEntity } from "../../../domain/entities/user.entity";
import { AuthRepositoryPort } from "../../ports/auth-repository.port";
import { TokenStoragePort } from "../../ports/token-storage.port";

export class SwitchRoleUseCase {
  constructor(
    private readonly authRepository: AuthRepositoryPort,
    private readonly tokenStorage: TokenStoragePort
  ) {}

  public async execute(): Promise<UserEntity> {
    const tokens = await this.authRepository.switchRole();
    this.tokenStorage.saveTokens(tokens);
    const user = await this.authRepository.getCurrentUser();
    return user;
  }
}
