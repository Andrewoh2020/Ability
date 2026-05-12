<script setup lang="ts">
import { useRoute } from 'vue-router';
import { reactive, ref, watch, onActivated, computed } from 'vue';
import { ArrowLeftIcon, CheckCircleIcon } from '@heroicons/vue/24/outline';

import router from '@/router';
import { routerBack } from '@/utils';
import { UserConnection } from '@/types/user';
import { useGetUserConnections, useFollowToggle } from '@/composables/user';

import DefaultAvatar from '@/components/DefaultAvatar.vue';
import Skeleton from '@/components/Skeleton.vue';

const route = useRoute();
const userId = route.params.id as string;
const initType = (['followers', 'following'].includes(route.query.type as string)
  ? route.query.type : 'followers') as 'followers' | 'following';

// Current active tab
const activeType = ref<'followers' | 'following'>(initType);

// Followers state
const followersParams = reactive({ type: 'followers' as const, page: 1 });
const followersList = ref<UserConnection[]>([]);
const followersHasMore = ref(true);
const followersTotal = ref<number>(0);

// Following state
const followingParams = reactive({ type: 'following' as const, page: 1 });
const followingList = ref<UserConnection[]>([]);
const followingHasMore = ref(true);
const followingTotal = ref<number>(0);

const followToggleRunning: Record<string, boolean> = {};
const { mutateAsync: followToggle } = useFollowToggle();

// Two independent queries
const { data: followersData, isLoading: followersLoading } = useGetUserConnections(userId, followersParams);
const { data: followingData, isLoading: followingLoading } = useGetUserConnections(userId, followingParams);

// Watch followers data changes
watch(followersData, (newData) => {
  if (newData) {
    followersTotal.value = newData.total;
    followersHasMore.value = newData.hasMore;
    followersList.value = [...followersList.value, ...newData.users];
  }
}, { immediate: true });

// Watch following data changes
watch(followingData, (newData) => {
  if (newData) {
    followingTotal.value = newData.total;
    followingHasMore.value = newData.hasMore;
    followingList.value = [...followingList.value, ...newData.users];
  }
}, { immediate: true });

// Computed properties for current display
const currentUsers = computed(() => activeType.value === 'followers' ? followersList.value : followingList.value);
const currentHasMore = computed(() => activeType.value === 'followers' ? followersHasMore.value : followingHasMore.value);
const isLoading = computed(() => activeType.value === 'followers' ? followersLoading.value : followingLoading.value);

const changeType = (value: 'followers' | 'following') => {
  if (activeType.value === value) return;
  activeType.value = value;
  router.replace({ query: { ...route.query, type: value } });
}

onActivated(() => {
  const queryType = route.query.type as string;
  const newType = (['followers', 'following'].includes(queryType) ? queryType : 'followers') as 'followers' | 'following';
  if (activeType.value !== newType) {
    changeType(newType);
  }
});

const clickFollowToggle = async (user: UserConnection) => {
  if (user.is_following === undefined || followToggleRunning[user.id]) return;
  try {
    followToggleRunning[user.id] = true;
    await followToggle(user.id);
    user.is_following = !user.is_following;
  } finally {
    followToggleRunning[user.id] = false;
  }
}

const loadMore = (event) => {
  if (isLoading.value || !currentHasMore.value) return;

  const container = event.target;
  const scrollHeight = container.scrollHeight;
  const scrollTop = container.scrollTop;
  const clientHeight = container.clientHeight;

  if (scrollHeight - scrollTop - clientHeight <= 120) {
    if (activeType.value === 'followers') {
      followersParams.page++;
    } else {
      followingParams.page++;
    }
  }
}
</script>

<template>
  <div class="flex-1 flex justify-center py-[16px] page-align">
    <div class="flex-1 flex flex-col gap-[24px] w-full max-w-[1080px] max-h-[85vh] py-[24px] rounded-[24px] bg-white shadow-md">
      <div
        class="flex items-center gap-[8px] px-[24px] leading-none cursor-pointer"
        @click="routerBack"
      >
        <ArrowLeftIcon class="size-[24px]" />
        <div class="text-[#3C518E] text-[24px]">
          Back
        </div>
      </div>
      <div class="flex min-h-[42px] px-[24px] switch">
        <div
          class="flex justify-center items-center gap-[8px] w-[137px] cursor-pointer leading-none item"
          :class="{active: activeType === 'followers'}"
          @click="changeType('followers')"
        >
          <div class="type">
            Followers
          </div>
          <div class="text-white text-[10px] py-[4px] px-[10px] rounded-[100px] bg-[#333333]">
            {{ followersTotal <= 99 ? followersTotal : '99+' }}
          </div>
        </div>
        <div
          class="flex justify-center items-center gap-[8px] w-[137px] cursor-pointer leading-none item"
          :class="{active: activeType === 'following'}"
          @click="changeType('following')"
        >
          <div class="type">
            Following
          </div>
          <div class="text-white text-[10px] py-[4px] px-[10px] rounded-[100px] bg-[#333333]">
            {{ followingTotal <= 99 ? followingTotal : '99+' }}
          </div>
        </div>
      </div>
      <div
        class="flex-1 flex flex-col gap-[24px] px-[24px] overflow-y-auto"
        @scroll="loadMore"
      >
        <template v-if="currentUsers.length">
          <RouterLink
            v-for="user in currentUsers"
            :key="user.id"
            :to="`/users/${user.id}/community`"
            class="flex items-center"
          >
            <img
              v-if="user.avatar_url"
              :src="user.avatar_url"
              class="size-[60px] mr-[8px] rounded-full"
            >
            <DefaultAvatar
              v-else
              class="size-[60px] mr-[8px] bg-[#F2F2F2]"
            />
            <div class="flex flex-col gap-[4px]">
              <div class="text-[20px] font-bold capitalize">
                {{ user.full_name || 'Anonymous' }}
              </div>
            </div>
            <div
              class="flex items-center gap-[8px] py-[8px] px-[12px] ml-auto cursor-pointer rounded-[40px] bg-[#333333]"
              :class="[user.is_following ? 'bg-[#CCCCCC]' : 'bg-[#333333]']"
              @click="clickFollowToggle(user)"
            >
              <CheckCircleIcon
                v-if="user.is_following"
                class="size-[24px] text-white"
              />
              <div class="text-white">
                {{ user.is_following ? 'Following' : 'Follow' }}
              </div>
            </div>
          </RouterLink>
        </template>
        <template v-else-if="isLoading && !(currentUsers.length)">
          <div
            v-for="_index in 4"
            :key="_index"
            class="flex items-center"
          >
            <Skeleton class="size-[60px] mr-[8px] bg-[#F2F2F2] rounded-full" />
            <Skeleton class="w-[100px] h-[25px] rounded-[4px]" />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .switch {
    .type {
      color: #999999;
    }
    .item.active {
      border-bottom: 1px solid #999999;
      .type {
        color: black;
        font-weight: bold;
      }
    }
  }
</style>
