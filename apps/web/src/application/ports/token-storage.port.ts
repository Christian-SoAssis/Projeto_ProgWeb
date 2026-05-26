import { AuthTokensVo } from "../../domain/value-objects/auth-tokens.vo";

export interface TokenStoragePort {
  getAccessToken(): string | null;
  getRefreshToken(): string | null;
  saveTokens(tokens: AuthTokensVo): void;
  clearTokens(): void;
}
