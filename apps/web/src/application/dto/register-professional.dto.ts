export interface RegisterProfessionalDto {
  readonly name: string;
  readonly email: string;
  readonly phone: string;
  readonly password: string;
  readonly consentTerms: boolean;
  readonly consentPrivacy: boolean;
  readonly bio: string;
  readonly latitude: number;
  readonly longitude: number;
  readonly serviceRadiusKm: number;
  readonly hourlyRateCents: number;
  readonly categoryIds: string[];
  readonly document: File;
}
