<script setup lang="ts">
import { ref } from 'vue';

import { App } from '@/types/app';

import AppItem from '@/components/AppItem.vue';
import AppItemSkeleton from '@/components/AppItemSkeleton.vue';

import tempCover from '@/assets/temp/cover.png';

const page = ref(1);
const hasMore = ref(true);
const loading = ref(false);
const apps = [
  {id: '', cover: tempCover, name: 'TasteMap', description: 'A sleek, modern, and fully customizable template for your next marketing website. Content powered by BaseHub.', category: 'productivity', favorites_count: 11200},
  {id: '', cover: tempCover, name: 'VideoCut', description: 'Transform your portraits into intimate and playful elevator moments with AI-powered precision. Create unique overhead angle shots that capture genuine emotion and spontaneous joy.', category: 'finance', favorites_count: 567},
  {id: '', cover: tempCover, name: 'FlightFix', description: 'Travel never been so easy before', category: 'education', favorites_count: 18300000},
  {id: '', cover: tempCover, name: 'HangSync', description: 'A sleek, modern, and fully customizable template for your next marketing website. Content powered by BaseHub.A modern dating website design', category: 'social', favorites_count: 9900},
] as App[];

const loadMore = () => {
  if (loading.value || !hasMore.value) return;
  page.value++;
}
</script>

<template>
  <div class="text-[20px] md:text-[24px] font-bold mb-[24px]">
    Favorites
  </div>
  <template v-if="apps.length">
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-x-[13px] md:gap-x-[32px] gap-y-[24px] mb-[24px]">
      <AppItem
        v-for="app in apps"
        :key="app.id"
        :data="app"
      />
    </div>
    <div
      v-if="hasMore"
      class="w-fit py-[8px] px-[24px] mx-auto cursor-pointer rounded-[20px] border-1"
      @click="loadMore"
    >
      Show more
    </div>
  </template>
  <div
    v-else-if="loading && !apps.length"
    class="grid md:grid-cols-2 lg:grid-cols-3 gap-x-[13px] md:gap-x-[32px] gap-y-[24px]"
  >
    <AppItemSkeleton
      v-for="_index in 3"
      :key="_index"
    />
  </div>
</template>

<style scoped>
</style>
