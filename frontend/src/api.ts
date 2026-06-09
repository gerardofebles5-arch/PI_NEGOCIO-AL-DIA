export interface User {
  id: number;
  email: string;
  name: string;
  picture: string;
  role: "admin" | "user";
  created_at: string;
  document_count?: number;
}

export interface ExtractionFields {
  emails: string[];
  phones: string[];
  dates: string[];
  rifs: string[];
  amounts: { value: number; currency: string; raw: string }[];
  total_amount: number;
  currencies: Record<string, number>;
  keywords: [string, number][];
}

export interface Extraction {
  raw_text: string;
  word_count: number;
  fields: ExtractionFields;
}

export interface DocumentItem {
  id: number;
  filename: string;
  content_type: string;
  kind: string;
  size_bytes: number;
  status: string;
  source: string;
  error: string;
  created_at: string;
  owner_email?: string | null;
}

export interface DocumentDetail extends DocumentItem {
  extraction: Extraction | null;
}

export interface Dashboard {
  total_documents: number;
  by_kind: Record<string, number>;
  total_amount: number;
  currencies: Record<string, number>;
  total_words: number;
  recent: DocumentItem[];
  insights: string[];
  top_keywords: [string, number][];
}

export interface AuthConfig {
  google_client_id: string;
  google_enabled: boolean;
  dev_login_enabled: boolean;
}

const TOKEN_KEY = "pinad_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  authConfig: () => request<AuthConfig>("/api/auth/config"),
  googleLogin: (credential: string) =>
    request<{ token: string; user: User }>("/api/auth/google", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ credential }),
    }),
  devLogin: (email: string, name?: string) =>
    request<{ token: string; user: User }>("/api/auth/dev", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, name }),
    }),
  me: () => request<User>("/api/auth/me"),
  dashboard: () => request<Dashboard>("/api/dashboard"),
  listDocuments: () => request<DocumentItem[]>("/api/documents"),
  getDocument: (id: number) => request<DocumentDetail>(`/api/documents/${id}`),
  deleteDocument: (id: number) =>
    request<void>(`/api/documents/${id}`, { method: "DELETE" }),
  uploadDocument: (file: File, source: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("source", source);
    return request<DocumentDetail>("/api/documents", {
      method: "POST",
      body: form,
    });
  },
  adminUsers: () => request<User[]>("/api/admin/users"),
  adminDocuments: () => request<DocumentDetail[]>("/api/admin/documents"),
  adminStats: () =>
    request<{
      total_users: number;
      total_admins: number;
      total_documents: number;
      total_amount: number;
    }>("/api/admin/stats"),
};
