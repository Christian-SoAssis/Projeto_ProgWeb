import { DomainError } from "../errors/domain.error";

export class AuthTokensVo {
  constructor(
    public readonly accessToken: string,
    public readonly refreshToken: string
  ) {
    if (!accessToken || !refreshToken) {
      throw new DomainError("Tokens de autenticação não podem ser vazios");
    }
  }
}
