const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  // Se for FormData (para upload), o fetch define o Content-Type automaticamente com o boundary
  if (options.body instanceof FormData) {
    if (headers["Content-Type"]) {
        // @ts-ignore
        delete headers["Content-Type"]
    }
  }

  const url = `${BASE_URL}${endpoint}`;
  console.log("🚀 [apiFetch] Fetching:", url, "with method:", options.method || "GET");
  console.log("🚀 [apiFetch] Headers:", headers);

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || "Erro na requisição")
  }

  return response.json()
}
