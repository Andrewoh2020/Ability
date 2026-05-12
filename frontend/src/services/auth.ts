import http from '@/utils/http';
import { BaseResponse } from '@/types';

export async function magiclinkLogin(email: string) {
  await http.post<BaseResponse>('/auth/magiclink', { email });
}

export async function googleLogin(code: string) {
  const response = await http.post<BaseResponse<{ access_token: string, refresh_token: string }>>('/auth/google', { code });
  return response.data.data;
}

export async function refreshToken(token: string) {
  const response = await http.post<BaseResponse<{ access_token: string, refresh_token: string }>>('/auth/refresh', { refresh_token: token });
  return response.data.data;
}
