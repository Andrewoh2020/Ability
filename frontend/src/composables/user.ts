import { computed } from 'vue';
import { useMutation, useQuery } from '@tanstack/vue-query';
import { checkFollow, followToggle, getUserConnections, getUserProfile } from '@/services/user';

export const useGetUserProfile = (enabled: boolean) => {
  return useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const profile = await getUserProfile();
      return profile;
    },
    enabled: enabled
  });
};

export const useGetUserConnections = (
  id: string,
  options: {
    page: number,
    type: 'followers' | 'following'
  }
) => {
  const { page: _, ...restOptions } = options;
  const queryParams = computed(() => ({
    page: options.page,
    type: options.type,
  }));
  return useQuery({
    queryKey: ['user', id, queryParams, 'connections'],
    queryFn: () => getUserConnections(id, queryParams.value),
    ...restOptions,
  });
}

export const useFollowToggle = () => {
  return useMutation({
    mutationFn: (id: string) => followToggle(id),
  });
}

export const useCheckFollow = (id: string) => {
  return useQuery({
    queryKey: ['user', id, 'check_follow'],
    queryFn: () => checkFollow(id),
  });
}
