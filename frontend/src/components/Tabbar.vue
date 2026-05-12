<script setup lang="ts">
import studioIcon from '@/assets/studio-icon.svg';
import exploreIcon from '@/assets/explore-icon.svg';
import exploreActiceIcon from '@/assets/explore-active-icon.svg';
import studioActiceIcon from '@/assets/studio-active-icon.svg';

import { useModalStore } from '@/stores/modal';

const modalStore = useModalStore();
</script>

<template>
  <div
    class="
      fixed left-0 bottom-0 flex md:hidden justify-center items-center gap-[24px] w-full bg-[#FFFFFF4D]
      pt-[8px] px-[12px] tabbar
    "
  >
    <RouterLink
      v-slot="{ isExactActive }"
      to="/"
      class="flex-1 flex flex-col justify-center items-center gap-[2px] py-[8px]"
    >
      <img
        :src="(isExactActive) ? exploreActiceIcon : exploreIcon"
        alt="Explore"
        class="size-[24px]"
      >
      <div
        class="text-[#3C518E] text-[14px]"
        :class="{'font-bold': isExactActive}"
      >
        Discover
      </div>
    </RouterLink>
    <img
      src="@/assets/create-icon.svg"
      class="size-[40px]"
      @click="modalStore.showCreateSection = true"
    >
    <RouterLink
      v-slot="{ isExactActive }"
      to="/myapps"
      class="flex-1 flex flex-col justify-center items-center gap-[2px] py-[8px]"
    >
      <img
        :src="(isExactActive) ? studioActiceIcon : studioIcon"
        alt="Myapps"
        class="size-[24px]"
      >
      <div
        class="text-[#3C518E] text-[14px]"
        :class="{'font-bold': isExactActive}"
      >
        My Apps
      </div>
    </RouterLink>
  </div>
  <div class="md:hidden tabbar-placeholder" />
</template>

<style scoped>
  .tabbar {
    height: calc(76px + env(safe-area-inset-bottom));
    padding-bottom: calc(8px + env(safe-area-inset-bottom));
  }
  .tabbar-placeholder {
    height: calc(76px + env(safe-area-inset-bottom));
  }
</style>
