import { computed, ComputedRef } from 'vue';
import { useQuery, useMutation } from '@tanstack/vue-query';
import { App, AppStage } from "@/types/app";
import {
  getMyApps, getAppDetail, createApp, updateApp, deleteApp, getAppSandboxInfo, getAppsByCommunity, getAppsByFeatured, getAppComments, createComment, deleteComment, getSubComments, getAppCommunityDetail, getAppsByUserId, checkAppLike, appLikeToggle, commentLikeToggle, bookmarkToggle, getAppsByMix, initAppInfo, generateIcon, getAppStage, previewAppSandbox,
} from '@/services/app';


export const useAppStage = (id: string, options: any = {}) => useQuery<AppStage>({
  queryKey: [`apps:${id}:stage`],
  queryFn: () => getAppStage(id),
  ...options,
});

export const useAppPreview = (id: string, options: any = {}) => useQuery<string>({
  queryKey: [`apps:${id}:preview`],
  queryFn: () => previewAppSandbox(id),
  ...options,
});

export const useGetMyApps = (
  options: {
    page: number,
    limit?: number,
    enabled?: boolean,
  }
) => {
  const { page: _, limit: __, ...restOptions } = options;
  const queryParams = computed(() => ({
    page: options.page,
    limit: options.limit,
  }));
  return useQuery({
    queryKey: ['apps', queryParams],
    queryFn: () => getMyApps(queryParams.value),
    ...restOptions,
  });
}

export const useGetAppDetail = (id: string) => {
  return useQuery({
    queryKey: ['app', id],
    queryFn: () => getAppDetail(id),
  });
}

export const useCreateApp = () => {
  return useMutation({
    mutationFn: () => createApp(),
  });
}

export const useUpdateApp = () => {
  return useMutation({
    mutationFn: (app: App) => updateApp(app),
  });
}

export const useDeleteApp = () => {
  return useMutation({
    mutationFn: (id: string) => deleteApp(id),
  });
}

export const useGetAppSandboxInfo = (options: {
  id: string;
  enabled?: boolean;
}) => {
  const { id, enabled = true, ...restOptions } = options;

  return useQuery({
    queryKey: [`apps:${id}:sandbox`],
    queryFn: async () => getAppSandboxInfo(id),
    enabled,
    ...restOptions,
  });
}

export const useGetAppsByCommunity = (options: {
  page: number,
  category?: string;
  size?: number;
}) => {
  return useQuery({
    queryKey: ['apps', 'community', options],
    queryFn: () => getAppsByCommunity({ ...options }),
  });
}

export const useGetAppsByFeatured = () => {
  return useQuery({
    queryKey: ['apps', 'featured'],
    queryFn: () => getAppsByFeatured(),
  });
}

export const useGetAppComments = (
  id: string,
  options: {
    page: number,
    limit?: number,
    enabled?: boolean,
  }
) => {
  const { page, limit, ...restOptions } = options;
  const queryParams = computed(() => ({
    page: options.page,
    limit: options.limit,
  }));
  return useQuery({
    queryKey: ['apps', 'comments', queryParams],
    queryFn: () => getAppComments(id, { page, limit }),
    ...restOptions,
  });
}

export const useCreateComment = () => {
  return useMutation({
    mutationFn: (data: {
      app_id: string,
      content: string,
      parent_id: string | null,
    }) => createComment(data),
  });
}

export const useDeleteComment = () => {
  return useMutation({
    mutationFn: (id: string) => deleteComment(id),
  });
}

export const useGetSubComments = (
  id: string,
  options?: {
    enabled?: boolean,
  }
) => {
  const { ...restOptions } = options;
  const queryParams = computed(() => ({
    id: id,
  }));
  return useQuery({
    queryKey: ['apps', 'sub_comments', queryParams],
    queryFn: () => getSubComments(id),
    ...restOptions,
    select: (data) => {
      console.log(data)
    }
  });
}

export const useGetAppCommunityDetail = (id: string) => {
  return useQuery({
    queryKey: ['app', id, 'community'],
    queryFn: () => getAppCommunityDetail(id),
  });
}

export const useGetAppsByUserId = (
  userIdGetter: () => string,
  params: {
    page: number,
  },
  enabled?: ComputedRef<boolean>,
) => {
  const userId = computed(userIdGetter);
  const queryParams = computed(() => ({
    page: params.page,
  }));
  return useQuery({
    queryKey: ['apps:user', userId, queryParams],
    queryFn: () => {
      return getAppsByUserId(userId.value, params);
    },
    enabled: computed(() => !!userId.value && (enabled?.value ?? true)),
  });
};

export const useAppLikeToggle = () => {
  return useMutation({
    mutationFn: (id: string) => appLikeToggle(id),
  });
}

export const useCommentLikeToggle = () => {
  return useMutation({
    mutationFn: (id: string) => commentLikeToggle(id),
  });
}

export const useCheckAppLike = (id: string) => {
  return useQuery({
    queryKey: ['app', id, 'check_like'],
    queryFn: () => checkAppLike(id),
  });
}

export const useBookmarkToggle = () => {
  return useMutation({
    mutationFn: (id: string) => bookmarkToggle(id),
  });
}

export const useGetAppsByMix = (
  userIdGetter: () => string | undefined,
  params: {
    page: number,
    limit?: number,
  },
  enabled?: ComputedRef<boolean>,
) => {
  const userId = computed(userIdGetter);
  const queryParams = computed(() => ({
    page: params.page,
    limit: params.limit,
    user_id: userId.value,
  }));
  return useQuery({
    queryKey: ['apps', 'collection', userId, queryParams],
    queryFn: () => getAppsByMix(queryParams.value),
    enabled: computed(() => enabled?.value ?? true),
  });
}

export const useInitAppInfo = () => {
  return useMutation({
    mutationFn: (data: { id: string, prompt: string }) => initAppInfo(data.id, data.prompt),
  });
}

export const useGenerateIcon = () => {
  return useMutation({
    mutationFn: (data: { id: string, prompt: string }) => generateIcon(data.id, data.prompt),
  });
}
