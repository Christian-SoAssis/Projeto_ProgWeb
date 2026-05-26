import { CategoryEntity } from "./category.entity";

export class ProfessionalEntity {
  constructor(
    public readonly id: string,
    public readonly userId: string,
    public readonly bio: string,
    public readonly latitude: number,
    public readonly longitude: number,
    public readonly serviceRadiusKm: number,
    public readonly reputationScore: number,
    public readonly isVerified: boolean,
    public readonly categories: CategoryEntity[],
    public readonly name?: string,
    public readonly email?: string,
    public readonly hourlyRateCents?: number
  ) {}
}
