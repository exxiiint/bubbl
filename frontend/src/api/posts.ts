import { apiClient, type Comment, type FeedResponse, type Post, type Trend } from './client';

export async function getFeed(limit = 20, offset = 0): Promise<FeedResponse> {
  const { data } = await apiClient.get<FeedResponse>('/feed', { params: { limit, offset } });
  return data;
}

export async function createPost(form: FormData): Promise<Post> {
  const { data } = await apiClient.post<Post>('/posts', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}

export async function getPost(postId: string): Promise<Post> {
  const { data } = await apiClient.get<Post>(`/posts/${postId}`);
  return data;
}

export async function deletePost(postId: string): Promise<void> {
  await apiClient.delete(`/posts/${postId}`);
}

export async function likePost(postId: string): Promise<Post> {
  const { data } = await apiClient.post<Post>(`/posts/${postId}/like`);
  return data;
}

export async function unlikePost(postId: string): Promise<Post> {
  const { data } = await apiClient.delete<Post>(`/posts/${postId}/like`);
  return data;
}

export async function listComments(postId: string): Promise<Comment[]> {
  const { data } = await apiClient.get<Comment[]>(`/posts/${postId}/comments`);
  return data;
}

export async function createComment(postId: string, text: string): Promise<Comment> {
  const { data } = await apiClient.post<Comment>(`/posts/${postId}/comments`, { text });
  return data;
}

export async function getTrends(): Promise<Trend[]> {
  const { data } = await apiClient.get<Trend[]>('/posts/trends');
  return data;
}
