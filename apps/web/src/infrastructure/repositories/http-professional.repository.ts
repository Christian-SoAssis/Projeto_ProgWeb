import { ProfessionalRepositoryPort } from "../../application/ports/professional-repository.port";
import { RegisterProfessionalDto } from "../../application/dto/register-professional.dto";
import { HttpClient } from "../http/http-client";
import { DomainError } from "../../domain/errors/domain.error";

export class HttpProfessionalRepository implements ProfessionalRepositoryPort {
  constructor(private readonly httpClient: HttpClient) {}

  public async register(dto: RegisterProfessionalDto): Promise<void> {
    try {
      const formData = new FormData();
      formData.append("name", dto.name);
      formData.append("email", dto.email);
      formData.append("phone", dto.phone);
      formData.append("password", dto.password);
      formData.append("consent_terms", String(dto.consentTerms));
      formData.append("consent_privacy", String(dto.consentPrivacy));
      formData.append("bio", dto.bio);
      formData.append("latitude", String(dto.latitude));
      formData.append("longitude", String(dto.longitude));
      formData.append("service_radius_km", String(dto.serviceRadiusKm));
      formData.append("hourly_rate_cents", String(dto.hourlyRateCents));
      formData.append("category_ids_json", JSON.stringify(dto.categoryIds));
      formData.append("document_type", "cpf");
      formData.append("document", dto.document);

      await this.httpClient.post<void>("/professionals", formData);
    } catch (error) {
      throw new DomainError(
        error instanceof Error ? error.message : "Falha ao registrar profissional"
      );
    }
  }
}
