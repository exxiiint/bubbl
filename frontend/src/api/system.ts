import { API_URL, apiClient, type SystemStats } from './client';

export async function getHealth(): Promise<{ status: string; service: string }> {
  const { data } = await apiClient.get('/health');
  return data;
}

export async function getStats(): Promise<SystemStats> {
  const { data } = await apiClient.get<SystemStats>('/system/stats');
  return data;
}

export const externalLinks = {
  swagger: API_URL.replace(/\/api$/, '/docs'),
  health: `${API_URL}/health`,
  minio: 'http://localhost:9001'
};
