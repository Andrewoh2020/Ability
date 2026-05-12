<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { ArrowRightIcon } from '@heroicons/vue/24/outline';

import { App } from '@/types/app';
import { useModalStore } from '@/stores/modal';
import { useGetMyApps } from '@/composables/app';

import AppItem from '@/components/AppItem.vue';
import AppItemSkeleton from '@/components/AppItemSkeleton.vue';

const apps = ref<App[]>([]);
const hasMore = ref(true);
const modalStore = useModalStore();

const { data: publicData, isFetching: loading } = useGetMyApps({page: 1, limit: 11});

watch(publicData, (newData) => {
  if (newData) {
    hasMore.value = newData.hasMore;
    apps.value = [...apps.value, ...newData.apps];
  }
}, {immediate: true});

const appsIcons = computed(() => {
  const icons: string[] = [];
  if (apps.value.length) {
    for (let index = apps.value.length - 1; index >= 0 && icons.length < 3; index--) {
      const app = apps.value[index]!;
      if (app.icon) {
        icons.unshift(app.icon);
      }
    }
  }
  return icons;
});

const uploadItem = (newData: App) => {
  const index = apps.value.findIndex(app => app.id === newData.id);
  apps.value[index] = {
    ...apps.value[index],
    ...newData
  };
}

const deleteItem = (id: string) => {
  const index = apps.value.findIndex(app => app.id === id);
  apps.value.splice(index, 1);
}
</script>

<template>
  <div class="flex flex-col gap-[16px]">
    <div
      v-if="loading || apps.length"
      class="layout-content"
    >
      <div class="flex justify-between items-center mb-[16px] md:mb-[24px]">
        <div class="text-[#3C518E] text-[20px] md:text-[24px] font-semibold">
          Created Apps
        </div>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-[12px] md:gap-[18px]">
        <template v-if="apps.length">
          <AppItem
            v-for="app in apps"
            :key="app.id"
            :data="app"
            type="vertical"
            :action="true"
            @updated="uploadItem"
            @deleted="deleteItem"
          />
          <div
            v-if="hasMore"
            class="relative flex flex-col justify-center items-center gap-[16px] w-[100%] h-[198px] px-[10px] pt-[30px] cursor-pointer rounded-[16px] app-shadow"
            @click="modalStore.openAppList('public');"
          >
            <div
              v-if="appsIcons.length > 1"
              class="flex -space-x-[40px] justify-center"
            >
              <img
                v-for="(icon, index) in appsIcons.slice(0, 3)"
                :key="index"
                :src="icon"
                class="size-[80px] rounded-full"
              >
            </div>
            <img
              v-else
              src="@/assets/app-icon.png"
              class="size-[80px] rounded-full"
            >
            <div class="flex justify-center items-center gap-[4px] mb-[34px]">
              <div class="text-[18px] font-bold text-center">
                See All
              </div>
              <ArrowRightIcon class="size-[16px] md:size-[19px]" />
            </div>
          </div>
        </template>
        <template v-else-if="loading && !(apps.length)">
          <AppItemSkeleton
            v-for="_index in 4"
            :key="_index"
            type="vertical"
          />
        </template>
      </div>
    </div>
    <div
      v-else
      class="flex flex-col justify-center items-center gap-[14px] pt-[64px]"
    >
      <img
        src="@/assets/empty.png"
        class="w-[126px] h-[102px]"
      >
      <div class="text-[18px] text-center">
        No apps created yet
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
