import axios from 'axios';

export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
export const TOKEN_KEY = 'socialgram_token';

export type User = {
  id: string;
  username: string;
  email?: string | null;
  display_name: string;
  bio?: string | null;
  avatar_url?: string | null;
  created_at?: string | null;
  posts_count: number;
  followers_count: number;
  following_count: number;
  is_following: boolean;
};

export type UserCompact = Pick<User, 'id' | 'username' | 'display_name' | 'avatar_url'>;

export type Post = {
  id: string;
  author: UserCompact;
  caption?: string | null;
  media_url: string;
  media_object_key: string;
  created_at: string;
  updated_at: string;
  likes_count: number;
  comments_count: number;
  liked_by_me: boolean;
};

export type FeedResponse = {
  items: Post[];
  limit: number;
  offset: number;
  total: number;
};

export type Comment = {
  id: string;
  user: UserCompact;
  post_id: string;
  text: string;
  created_at: string;
};

export type NotificationItem = {
  id: string;
  type: string;
  actor: UserCompact | null;
  post_id?: string | null;
  comment_id?: string | null;
  is_read: boolean;
  created_at: string;
  text: string;
};

export type NotificationsResponse = {
  items: NotificationItem[];
  unread_count: number;
};

export type SystemStats = {
  users_count: number;
  posts_count: number;
  likes_count: number;
  comments_count: number;
  reports_count: number;
};

export type Trend = {
  tag: string;
  posts_count: number;
};

export type Report = {
  id: string;
  post_id: string;
  reporter: UserCompact;
  reason: string;
  details?: string | null;
  status: string;
  created_at: string;
  reviewed_at?: string | null;
  post_caption?: string | null;
  post_media_url?: string | null;
};

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
    return Promise.reject(error);
  }
);

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }
  return 'Что-то пошло не так. Попробуйте ещё раз.';
}
