<script setup lang="ts">
import { useModalStore } from '@/stores/modal';

import studioIcon from '@/assets/studio-icon.svg';
import exploreIcon from '@/assets/explore-icon.svg';
import exploreActiceIcon from '@/assets/explore-active-icon.svg';
import studioActiceIcon from '@/assets/studio-active-icon.svg';

import BaseLayout from '@/layouts/Base.vue';

const menus = [
  { route: '/', icon: exploreIcon, name: 'Discover', activeIcon: exploreActiceIcon, },
  { route: '/myapps', icon: studioIcon, name: 'My Apps', activeIcon: studioActiceIcon, },
];

const modalStore = useModalStore();
</script>

<template>
  <BaseLayout>
    <div class="flex gap-[16px] px-[16px] py-[24px]">
      <div class="hidden md:flex w-[104px] self-start sticky top-[88px] drawer drawer-open">
        <input
          id="drawer"
          type="checkbox"
          class="drawer-toggle"
        >
        <div class="!relative !w-full p-[12px] rounded-[16px] bg-white drawer-side">
          <div class="flex flex-col w-full h-full p-0 ">
            <div class="flex flex-col gap-[12px]">
              <div
                class="flex flex-col justify-center items-center gap-[4px] py-[8px] cursor-pointer"
                @click="modalStore.showCreateSection = true"
              >
                <img
                  src="@/assets/create-icon.svg"
                  class="size-[40px]"
                >
                <div class="text-[14px]">
                  Create
                </div>
              </div>
              <template
                v-for="menu in menus"
                :key="menu.name"
              >
                <RouterLink
                  v-slot="{ isExactActive }"
                  :to="menu.route"
                  exact-active-class="active-menu"
                  class="flex flex-col justify-center items-center gap-[4px] py-[8px]"
                >
                  <img
                    :src="(isExactActive) ? menu.activeIcon : menu.icon"
                    :alt="menu.name"
                    class="size-[24px]"
                  >
                  <div class="text-[14px] text-center name">
                    {{ menu.name }}
                  </div>
                </RouterLink>
              </template>
            </div>
          </div>
        </div>
      </div>
      <div class="flex-1 flex flex-col min-w-0">
        <RouterView />
      </div>
    </div>
  </BaseLayout>
</template>

<style scoped>
  .drawer-side {
    height: calc(100vh - 64px - 48px);
    box-shadow: 0px 4px 60px 0px #0000000D;
    .active-menu {
      border-radius: 16px;
      box-shadow: 0px 4px 60px 0px #0000000D;
      .name {
        font-weight: bold;
      }
    }
  }
</style>
