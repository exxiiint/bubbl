import { apiClient, type Post, type User } from './client';

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/users/me');
  return data;
}

export async function updateMe(form: FormData): Promise<User> {
  const { data } = await apiClient.patch<User>('/users/me', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}

export async function getUser(username: string): Promise<User> {
  const { data } = await apiClient.get<User>(`/users/${username}`);
  return data;
}

export async function searchUsers(q: string): Promise<User[]> {
  const { data } = await apiClient.get<User[]>('/users/search', { params: { q } });
  return data;
}

export async function followUser(userId: string): Promise<User> {
  const { data } = await apiClient.post<User>(`/users/${userId}/follow`);
  return data;
}

export async function unfollowUser(userId: string): Promise<User> {
  const { data } = await apiClient.delete<User>(`/users/${userId}/follow`);
  return data;
}

export async function getUserPosts(userId: string): Promise<Post[]> {
  const { data } = await apiClient.get<Post[]>(`/users/${userId}/posts`);
  return data;
}
