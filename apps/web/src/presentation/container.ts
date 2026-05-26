import { API_BASE_URL } from "../infrastructure/http/api-config";
import { HttpClient } from "../infrastructure/http/http-client";
import { LocalTokenStorage } from "../infrastructure/storage/local-token-storage";
import { HttpAuthRepository } from "../infrastructure/repositories/http-auth.repository";
import { HttpProfessionalRepository } from "../infrastructure/repositories/http-professional.repository";

import { LoginUseCase } from "../application/use-cases/auth/login.use-case";
import { RegisterClientUseCase } from "../application/use-cases/auth/register-client.use-case";
import { RegisterProfessionalUseCase } from "../application/use-cases/auth/register-professional.use-case";
import { LogoutUseCase } from "../application/use-cases/auth/logout.use-case";
import { GetCurrentUserUseCase } from "../application/use-cases/auth/get-current-user.use-case";
import { SwitchRoleUseCase } from "../application/use-cases/auth/switch-role.use-case";
import { OauthLoginUseCase } from "../application/use-cases/auth/oauth-login.use-case";

// 1. Instanciação dos Drivers e Interface Adapters concretos
const httpClient = new HttpClient(API_BASE_URL);
const tokenStorage = new LocalTokenStorage();
const authRepository = new HttpAuthRepository(httpClient);
const professionalRepository = new HttpProfessionalRepository(httpClient);

// 2. Instanciação e injeção de dependências nos Casos de Uso
export const loginUseCase = new LoginUseCase(authRepository, tokenStorage);
export const registerClientUseCase = new RegisterClientUseCase(authRepository, tokenStorage);
export const registerProfessionalUseCase = new RegisterProfessionalUseCase(
  professionalRepository,
  authRepository,
  tokenStorage
);
export const logoutUseCase = new LogoutUseCase(tokenStorage);
export const getCurrentUserUseCase = new GetCurrentUserUseCase(authRepository, tokenStorage);
export const switchRoleUseCase = new SwitchRoleUseCase(authRepository, tokenStorage);
export const oauthLoginUseCase = new OauthLoginUseCase(authRepository, tokenStorage);
