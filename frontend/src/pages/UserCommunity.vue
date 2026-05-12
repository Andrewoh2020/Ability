<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { CheckCircleIcon, PencilSquareIcon } from '@heroicons/vue/24/outline';

import { App } from '@/types/app';
import { formatNumber } from '@/utils';
import { UserCommunity } from '@/types/user';
import { useUserStore } from '@/stores/user';
import { useModalStore } from '@/stores/modal';
import { useFollowToggle } from '@/composables/user';
import { useGetAppsByUserId, useGetAppsByMix } from '@/composables/app';
import { getUserCommunityProfile } from '@/services/user';

import AppItem from '@/components/AppItem.vue';
import DefaultAvatar from '@/components/DefaultAvatar.vue';
import AppItemSkeleton from '@/components/AppItemSkeleton.vue';

const route = useRoute();
const userStore = useUserStore();
const modalStore = useModalStore();
const getUserId = () => {
  return (route.params.id as string) || userStore.profile?.id || '';
}
const userId = computed(getUserId);
const userData = ref<{ profile: UserCommunity, is_following: boolean }>();
const { mutateAsync: followToggle } = useFollowToggle();

// Current active tab
const activeTab = ref<'apps' | 'collection'>('apps');

// Apps state
const appsParams = reactive({ page: 1 });
const appsList = ref<App[]>([]);
const appsHasMore = ref(true);
const appsTotal = ref<number>(0);

// Collection state
const collectionParams = reactive({ page: 1 });
const collectionList = ref<App[]>([]);
const collectionHasMore = ref(true);
const collectionTotal = ref<number>(0);

// Two independent queries
const { data: appsData, isFetching: appsLoading } = useGetAppsByUserId(getUserId, appsParams);
const { data: collectionData, isFetching: collectionLoading } = useGetAppsByMix(getUserId, collectionParams);

// Watch apps data changes
watch(
  [appsLoading, appsData],
  ([newLoading, newData], [oldLoading]) => {
    const finishedLoading = oldLoading && !newLoading;
    const dataUpdatedWhileNotLoading = !newLoading && newData;
    if (finishedLoading || dataUpdatedWhileNotLoading) {
      if (newData) {
        if (appsParams.page === 1) {
          appsList.value = newData.apps;
        } else {
          appsList.value = [...appsList.value, ...newData.apps];
        }
        appsHasMore.value = newData.hasMore;
        appsTotal.value = newData.total;
      }
    }
  },
  { immediate: true }
);

// Watch collection data changes
watch(
  [collectionLoading, collectionData],
  ([newLoading, newData], [oldLoading]) => {
    const finishedLoading = oldLoading && !newLoading;
    const dataUpdatedWhileNotLoading = !newLoading && newData;
    if (finishedLoading || dataUpdatedWhileNotLoading) {
      if (newData) {
        if (collectionParams.page === 1) {
          collectionList.value = newData.apps;
        } else {
          collectionList.value = [...collectionList.value, ...newData.apps];
        }
        collectionHasMore.value = newData.hasMore;
        collectionTotal.value = newData.total;
      }
    }
  },
  { immediate: true }
);

// Computed properties for current display
const currentApps = computed(() => activeTab.value === 'apps' ? appsList.value : collectionList.value);
const currentHasMore = computed(() => activeTab.value === 'apps' ? appsHasMore.value : collectionHasMore.value);
const listLoading = computed(() => activeTab.value === 'apps' ? appsLoading.value : collectionLoading.value);

watch(userId, async (newData) => {
  if (newData) {
    userData.value = await getUserCommunityProfile(newData);
  }
}, { immediate: true });

watch(() => userStore.profile, (newProfile) => {
  if (newProfile && userData.value && userId.value === newProfile.id) {
    userData.value.profile = {
      ...userData.value.profile,
      ...newProfile,
    };
  }
}, { deep: true });

const clickFollowToggle = async () => {
  if (!userData.value) return
  await followToggle(userId.value);
  userData.value.is_following = !userData.value.is_following;
  userData.value.profile.followers_count += userData.value.is_following ? 1 : -1;
}

const switchTab = (tab: 'apps' | 'collection') => {
  if (activeTab.value === tab) return;
  activeTab.value = tab;
}

const loadMore = (event: Event) => {
  if (listLoading.value || !currentHasMore.value) return;

  const container = event.target as HTMLElement;
  const scrollHeight = container.scrollHeight;
  const scrollTop = container.scrollTop;
  const clientHeight = container.clientHeight;

  if (scrollHeight - scrollTop - clientHeight <= 120) {
    if (activeTab.value === 'apps') {
      appsParams.page++;
    } else {
      collectionParams.page++;
    }
  }
}

const deleteItem = (id: string) => {
  if (activeTab.value === 'apps') {
    const index = appsList.value.findIndex(app => app.id === id);
    if (index !== -1) appsList.value.splice(index, 1);
  } else {
    const index = collectionList.value.findIndex(app => app.id === id);
    if (index !== -1) collectionList.value.splice(index, 1);
  }
}
</script>

<template>
  <div
    v-if="userData"
    class="flex justify-center pt-[16px] page-align"
  >
    <div class="flex flex-col w-full max-w-[1080px] max-h-[85vh] pt-[16px] md:pt-[24px] rounded-[24px] bg-white">
      <div class="flex flex-col gap-[16px] px-[24px] mb-[16px] md:mb-[24px]">
        <div class="flex items-center">
          <img
            v-if="userData.profile.avatar_url"
            :src="userData.profile.avatar_url"
            class="size-[60px] mr-[8px] rounded-full"
          >
          <DefaultAvatar
            v-else
            class="size-[60px] mr-[8px] bg-[#F2F2F2]"
          />
          <div class="flex flex-col gap-[4px]">
            <div class="text-[20px] font-bold capitalize">
              {{ userData.profile.full_name || 'Anonymous' }}
            </div>
          </div>
          <div
            v-if="userStore.profile?.id && userData.profile.id === userStore.profile?.id"
            class="flex items-center gap-[8px] py-[8px] px-[12px] ml-auto cursor-pointer rounded-[40px] bg-[#333333]"
            @click="modalStore.showEditProfile = true"
          >
            <PencilSquareIcon class="size-[16px] text-white" />
            <div class="text-white">
              Edit
            </div>
          </div>
          <div
            v-else-if="userStore.profile?.id"
            class="flex items-center gap-[8px] py-[8px] px-[12px] ml-auto cursor-pointer rounded-[40px]"
            :class="[userData.is_following ? 'bg-[#CCCCCC]' : 'bg-[#333333]']"
            @click="clickFollowToggle"
          >
            <CheckCircleIcon
              v-if="userData.is_following"
              class="size-[24px] text-white"
            />
            <div class="text-white">
              {{ userData.is_following ? 'Following' : 'Follow' }}
            </div>
          </div>
        </div>
        <div class="flex items-center">
          <RouterLink
            :to="`/users/${userId}/connections?type=followers`"
            class="flex items-center"
          >
            <div class="text-[#999999] mr-[4px]">
              Followers
            </div>
            <div class="font-bold">
              {{ formatNumber(userData.profile.followers_count) }}
            </div>
          </RouterLink>
          <div class="w-[1px] h-[80%] mx-[8px] bg-[#999999]" />
          <RouterLink
            :to="`/users/${userId}/connections?type=following`"
            class="flex items-center"
          >
            <div class="text-[#999999] mr-[4px]">
              Following
            </div>
            <div class="font-bold">
              {{ formatNumber(userData.profile.following_count) }}
            </div>
          </RouterLink>
        </div>
        <div
          v-if="userData.profile.bio"
          class="text-[18px]"
        >
          {{ userData.profile.bio }}
        </div>
      </div>
      <div class="flex min-h-[42px] switch px-[24px]">
        <div
          class="flex justify-center items-center gap-[8px] w-[155px] cursor-pointer leading-none item"
          :class="{ active: activeTab === 'apps' }"
          @click="switchTab('apps')"
        >
          <div class="type">
            Created Apps
          </div>
          <div
            v-if="appsTotal"
            class="text-white text-[10px] py-[4px] px-[10px] rounded-[100px] bg-[#333333]"
          >
            {{ appsTotal <= 99 ? appsTotal : '99+' }}
          </div>
        </div>
        <div
          class="flex justify-center items-center gap-[8px] w-[155px] cursor-pointer leading-none item"
          :class="{ active: activeTab === 'collection' }"
          @click="switchTab('collection')"
        >
          <div class="type">
            Collection
          </div>
          <div
            v-if="collectionTotal"
            class="text-white text-[10px] py-[4px] px-[10px] rounded-[100px] bg-[#333333]"
          >
            {{ collectionTotal <= 99 ? collectionTotal : '99+' }}
          </div>
        </div>
      </div>
      <div
        class="flex-1 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-x-[14px] gap-y-[24px] p-[16px] md:p-[24px] overflow-y-auto"
        @scroll="loadMore"
      >
        <template v-if="currentApps.length">
          <AppItem
            v-for="app in currentApps"
            :key="app.id"
            :data="app"
            type="vertical"
            :action="activeTab === 'apps' && userId === userStore.profile?.id"
            @deleted="deleteItem"
          />
        </template>
        <template v-else-if="listLoading && !(currentApps.length)">
          <AppItemSkeleton
            v-for="_index in 10"
            :key="_index"
            type="vertical"
          />
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
