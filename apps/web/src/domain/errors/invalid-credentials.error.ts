import { DomainError } from "./domain.error";

export class InvalidCredentialsError extends DomainError {
  constructor(message: string = "Credenciais inválidas") {
    super(message);
    this.name = "InvalidCredentialsError";
    Object.setPrototypeOf(this, new.target.prototype);
  }
}
