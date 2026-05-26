import { DomainError } from "../errors/domain.error";

export class EmailVo {
  public readonly value: string;

  constructor(value: string) {
    if (!this.validate(value)) {
      throw new DomainError("Endereço de e-mail inválido");
    }
    this.value = value.toLowerCase().trim();
  }

  private validate(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}
