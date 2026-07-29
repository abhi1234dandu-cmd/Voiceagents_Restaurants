const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.API_BASE_URL || "http://localhost:8000";

export function getDevToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("hostline_dev_token");
}

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit & { token?: string | null } = {}
): Promise<T> {
  const { token, ...init } = options;
  const auth = token ?? getDevToken();
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (auth) headers.set("Authorization", `Bearer ${auth}`);
  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export { API_URL };
