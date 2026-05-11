import { apiClient, type NotificationsResponse } from './client';

export async function getNotifications(): Promise<NotificationsResponse> {
  const { data } = await apiClient.get<NotificationsResponse>('/notifications');
  return data;
}

export async function readAllNotifications(): Promise<NotificationsResponse> {
  const { data } = await apiClient.post<NotificationsResponse>('/notifications/read-all');
  return data;
}
