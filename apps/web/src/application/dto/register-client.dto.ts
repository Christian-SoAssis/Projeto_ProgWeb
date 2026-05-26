export interface RegisterClientDto {
  readonly name: string;
  readonly email: string;
  readonly phone: string;
  readonly password: string;
  readonly consentTerms: boolean;
  readonly consentPrivacy: boolean;
}
