import { apiClient, type Report } from './client';

export async function createReport(postId: string, reason: string, details?: string): Promise<Report> {
  const { data } = await apiClient.post<Report>(`/posts/${postId}/report`, { reason, details });
  return data;
}

export async function getReports(status?: string): Promise<Report[]> {
  const { data } = await apiClient.get<Report[]>('/admin/reports', { params: { status } });
  return data;
}

export async function markReportReviewed(reportId: string): Promise<Report> {
  const { data } = await apiClient.post<Report>(`/admin/reports/${reportId}/reviewed`);
  return data;
}
