import { TokenStoragePort } from "../../ports/token-storage.port";

export class LogoutUseCase {
  constructor(private readonly tokenStorage: TokenStoragePort) {}

  public execute(): void {
    this.tokenStorage.clearTokens();
  }
}
