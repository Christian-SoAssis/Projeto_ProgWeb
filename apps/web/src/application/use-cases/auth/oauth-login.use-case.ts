import { UserEntity } from "../../../domain/entities/user.entity";
import { AuthTokensVo } from "../../../domain/value-objects/auth-tokens.vo";
import { AuthRepositoryPort } from "../../ports/auth-repository.port";
import { TokenStoragePort } from "../../ports/token-storage.port";

export class OauthLoginUseCase {
  constructor(
    private readonly authRepository: AuthRepositoryPort,
    private readonly tokenStorage: TokenStoragePort
  ) {}

  public async execute(accessToken: string, refreshToken: string): Promise<UserEntity> {
    const tokens = new AuthTokensVo(accessToken, refreshToken);
    this.tokenStorage.saveTokens(tokens);
    const user = await this.authRepository.getCurrentUser();
    return user;
  }
}
