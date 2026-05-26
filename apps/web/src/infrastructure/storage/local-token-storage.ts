import { TokenStoragePort } from "../../application/ports/token-storage.port";
import { AuthTokensVo } from "../../domain/value-objects/auth-tokens.vo";

export class LocalTokenStorage implements TokenStoragePort {
  public getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  public getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("refresh_token");
  }

  public saveTokens(tokens: AuthTokensVo): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("access_token", tokens.accessToken);
    localStorage.setItem("refresh_token", tokens.refreshToken);
    
    // Sincronizar cookie do lado do cliente para o middleware
    document.cookie = `access_token=${tokens.accessToken}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Strict`;
  }

  public clearTokens(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  }
}
