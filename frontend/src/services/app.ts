import http from '@/utils/http';
import { BaseResponse, Message } from "@/types";
import { App, AppComment, AppCommunityDetail, AppDetail, AppSubComment, AppStage, ChatEvent } from "@/types/app";

interface AppSandboxInfo {
  status: 0 | 1 | 2;
  public_url?: string;
}

export async function getAppStage(id: string) {
  const response = await http.get<BaseResponse<AppStage>>(`/apps/${id}/stage`);
  return response.data.data;
}

export async function getAppSandboxInfo(id: string): Promise<AppSandboxInfo> {
  const response = await http.get(`/apps/${id}/sandbox`);
  return response.data.data;
}

export async function getMyApps(params: {
  page: number,
  limit?: number,
}) {
  const response = await http.get<BaseResponse<{ apps: App[], hasMore: boolean }>>(`/apps`, { params });
  return response.data.data;
}

export async function getAppDetail(id: string) {
  const response = await http.get<BaseResponse<{ app: AppDetail }>>(`/apps/${id}`);
  return response.data.data.app;
}

export async function createApp() {
  const response = await http.post<BaseResponse<{ id: string }>>('/apps');
  return response.data.data.id;
}

export async function updateApp(app: App) {
  await http.put<BaseResponse>(`/apps/${app.id}`, app);
}

export async function deleteApp(id: string) {
  await http.delete<BaseResponse>(`/apps/${id}`);
}

export async function getAppMessages(id: string): Promise<Message[]> {
  const response = await http.get(`/apps/${id}/messages`);
  return response.data.data;
}

export async function getAppEvents(id: string): Promise<ChatEvent[]> {
  const response = await http.get(`/apps/${id}/events`);
  return response.data.data;
}

export async function previewAppSandbox(id: string): Promise<string> {
  const response = await http.post(`/apps/${id}/sandbox/actions/preview`);
  return response.data.data;
}

export async function getAppsByFeatured(): Promise<App[]> {
  const response = await http.get(`/feeds/featured`);
  return response.data.data;
}

export async function getAppsByCommunity(params: {
  page: number,
  category?: string;
  size?: number;
}): Promise<{ apps: App[], hasMore: boolean }> {
  const response = await http.get(`/feeds/discovered`, { params });
  return response.data.data;
}

export async function getAppComments(id: string, params: {
  page: number,
  limit?: number,
}): Promise<{ data: AppComment[], total: number }> {
  const response = await http.get(`/apps/${id}/comments`, {
    params: {
      page: params.page,
      size: params.limit
    }
  });
  return response.data.data;
}

export async function createComment(data: {
  app_id: string,
  content: string,
  parent_id: string | null,
}): Promise<string> {
  const response = await http.post<BaseResponse<{ id: string }>>('/comments', data);
  return response.data.data.id;
}

export async function deleteComment(id: string): Promise<void> {
  await http.delete(`/comments/${id}`);
}

export async function getSubComments(id: string): Promise<AppSubComment[]> {
  const response = await http.get(`/comments/${id}/replies`);
  return response.data.data;
}

export async function getAppCommunityDetail(id: string) {
  const response = await http.get<BaseResponse<{ app: AppCommunityDetail }>>(`/apps/${id}/community`);
  return response.data.data.app;
}

export async function getAppsByUserId(
  userId: string,
  params: {
    page: number,
  }
) {
  const response = await http.get<BaseResponse<{ apps: App[], total: number, hasMore: boolean }>>(`/apps/users/${userId}`, { params });
  return response.data.data;
}

export async function appLikeToggle(id: string) {
  await http.post(`/apps/${id}/like`);
}

export async function commentLikeToggle(id: string) {
  await http.post(`/comments/${id}/like`);
}

export async function checkAppLike(id: string) {
  const response = await http.get<BaseResponse<{ is_like: boolean }>>(`/apps/${id}/check_like`);
  return response.data.data.is_like;
}

export async function bookmarkToggle(id: string) {
  await http.post(`/apps/${id}/bookmarks`);
}

export async function getAppsByMix(params: {
  page: number,
  limit?: number,
  user_id?: string,
}) {
  const response = await http.get<BaseResponse<{ apps: App[], hasMore: boolean, total: number }>>(`/apps/mix`, { params });
  return response.data.data;
}

export async function initAppInfo(id: string, prompt: string) {
  const response = await http.post<BaseResponse<{ name: string, description: string, category: string, icon: string }>>(`/apps/${id}/init`, { prompt });
  return response.data.data;
}

export async function generateIcon(id: string, prompt: string) {
  const response = await http.post<BaseResponse<{ url: string }>>(`/apps/${id}/icon`, { prompt });
  return response.data.data.url;
}

