export class UserEntity {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly email: string,
    public readonly role: "client" | "professional",
    public readonly avatarUrl?: string
  ) {}
}
