import { UserEntity } from "../../domain/entities/user.entity";

export interface RawUserDto {
  id: string;
  name: string;
  email: string;
  role: "client" | "professional";
  avatar_url?: string;
}

export class UserMapper {
  public static toDomain(raw: RawUserDto): UserEntity {
    return new UserEntity(
      raw.id,
      raw.name,
      raw.email,
      raw.role,
      raw.avatar_url
    );
  }
}
