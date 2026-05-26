import { UserEntity } from "../../../domain/entities/user.entity";
import { AuthRepositoryPort } from "../../ports/auth-repository.port";
import { TokenStoragePort } from "../../ports/token-storage.port";

export class GetCurrentUserUseCase {
  constructor(
    private readonly authRepository: AuthRepositoryPort,
    private readonly tokenStorage: TokenStoragePort
  ) {}

  public async execute(): Promise<UserEntity | null> {
    const token = this.tokenStorage.getAccessToken();
    if (!token) {
      return null;
    }
    return this.authRepository.getCurrentUser();
  }
}
