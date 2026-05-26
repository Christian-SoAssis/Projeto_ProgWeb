import { HttpError } from "./http.error";

export class HttpClient {
  constructor(private readonly baseUrl: string) {}

  public async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers as Record<string, string>),
    };

    if (options.body instanceof FormData) {
      delete headers["Content-Type"];
    }

    const url = `${this.baseUrl}${endpoint}`;
    console.log("🚀 [HttpClient] Requesting:", url, "with method:", options.method || "GET");

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new HttpError(
          response.status,
          errorData.detail || "Erro na requisição"
        );
      }

      return response.json() as Promise<T>;
    } catch (error) {
      if (error instanceof HttpError) {
        throw error;
      }
      throw new HttpError(500, error instanceof Error ? error.message : "Erro de rede desconhecido");
    }
  }

  public async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  public async post<T>(endpoint: string, body?: any, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body),
    });
  }
}

import { API_BASE_URL } from "./api-config";
const defaultHttpClient = new HttpClient(API_BASE_URL);
export async function apiFetch(endpoint: string, options: RequestInit = {}): Promise<any> {
  return defaultHttpClient.request(endpoint, options);
}
