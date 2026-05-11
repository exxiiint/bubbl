import { apiClient, TOKEN_KEY, type User } from './client';

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type RegisterPayload = {
  username: string;
  email: string;
  password: string;
  display_name: string;
};

export async function register(payload: RegisterPayload): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/register', payload);
  localStorage.setItem(TOKEN_KEY, data.access_token);
  return data;
}

export async function login(loginValue: string, password: string): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/login', { login: loginValue, password });
  localStorage.setItem(TOKEN_KEY, data.access_token);
  return data;
}

export async function me(): Promise<User> {
  const { data } = await apiClient.get<User>('/auth/me');
  return data;
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
