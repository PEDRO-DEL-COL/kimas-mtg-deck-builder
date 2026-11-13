const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { Accept: 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    throw new Error(`Erro na API: ${response.status} ${response.statusText}`)
  }
  return (await response.json()) as T
}

export interface HealthResponse {
  status: string
}

export function getHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>('/health')
}
