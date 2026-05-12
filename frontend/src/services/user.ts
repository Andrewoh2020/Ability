import http from '@/utils/http';
import { BaseResponse } from "@/types";
import { User, UserCommunity, UserConnection } from "@/types/user";

export async function getUserProfile() {
  const response = await http.get<BaseResponse<{ profile: User }>>("/users/me");
  return response.data.data.profile;
}

export async function updateUserInfo(formData: FormData) {
  const response = await http.put<BaseResponse<Partial<User>>>("/users/me", formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data.data;
}

export async function getUserCommunityProfile(id: string) {
  const response = await http.get<BaseResponse<{ profile: UserCommunity, is_following: boolean }>>(`/users/${id}`);
  return response.data.data;
}

export async function getUserConnections(
  id: string,
  params: {
    page: number,
    type: 'followers' | 'following',
  }
) {
  const response = await http.get<BaseResponse<{ users: UserConnection[], total: number, hasMore: boolean }>>(`/users/${id}/connections`, {params});
  return response.data.data;
}

export async function followToggle(id: string) {
  await http.post(`/users/${id}/follow`);
}

export async function checkFollow(id: string) {
  const response = await http.get<BaseResponse<{ is_following: boolean }>>(`/users/${id}/check_follow`);
  return response.data.data.is_following;
}
