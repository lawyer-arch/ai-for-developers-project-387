import { TokenResponse, User } from "./types";

const TOKEN_KEY = "scheduling_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export function getAuthHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function login(
  username: string,
  password: string
): Promise<TokenResponse> {
  const response = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Login failed");
  }
  const data: TokenResponse = await response.json();
  setToken(data.access_token);
  return data;
}

export async function register(
  username: string,
  email: string,
  password: string,
  name?: string,
  timeZone?: string
): Promise<TokenResponse> {
  const response = await fetch("/api/v1/auth", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password, name, timeZone }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Registration failed");
  }
  const data: TokenResponse = await response.json();
  setToken(data.access_token);
  return data;
}

export async function getMe(): Promise<User> {
  const response = await fetch("/api/v1/auth/me", {
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
  });
  if (!response.ok) {
    throw new Error("Not authenticated");
  }
  return response.json();
}

export function logout(): void {
  removeToken();
  window.location.href = "/auth/login";
}
