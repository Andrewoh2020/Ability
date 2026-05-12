<script setup lang="ts">
import { watch } from 'vue';
import { UserIcon } from '@heroicons/vue/24/solid';
import { ArrowUpTrayIcon } from '@heroicons/vue/24/outline';

import router from '@/router';
import { closeDropdown } from '@/utils';
import { useUserStore } from '@/stores/user';
import { useGetUserProfile } from '@/composables/user';

import Logo from '@/components/Logo.vue';
import DefaultAvatar from '@/components/DefaultAvatar.vue';

const userStore = useUserStore();
const {data: profile} = useGetUserProfile(!!userStore.token && !userStore.profile);

watch(profile, (newProfile) => {
  userStore.profile = newProfile!;
});

const logout = () => {
  userStore.logout();
  router.push({path: '/'});
}
</script>

<template>
  <header
    id="header"
    class="fixed top-0 left-0 right-0 z-100 flex justify-between items-center h-[64px] py-[8px] page-align"
  >
    <div class="flex items-center gap-[12px]">
      <RouterLink to="/">
        <Logo />
      </RouterLink>
    </div>
    <div class="flex items-center gap-[16px] ml-auto">
      <RouterLink to="/login" class="text-[14px] font-normal py-[6px] px-[16px] md:py-[14px] md:px-[24px] rounded-[40px] bg-white btn" v-if="!userStore.profile">
        Get started
      </RouterLink>
      <div class="dropdown dropdown-end" v-else>
        <div tabindex="0" role="button" class="cursor-pointer">
          <img :src="userStore.profile.avatar_url" class="size-[48px] rounded-full" v-if="userStore.profile.avatar_url">
          <DefaultAvatar class="size-[48px] bg-white" v-else/>
        </div>
        <div tabindex="0" class="w-[280px] p-[16px] mt-[8px] rounded-[16px] bg-white shadow-md dropdown-content">
          <div class="flex justify-between items-center gap-[8px] pb-[24px] mb-[24px] border-b-[1px] border-b-[#CCCCCC]">
            <img :src="userStore.profile.avatar_url" class="size-[48px] rounded-full" v-if="userStore.profile.avatar_url">
            <DefaultAvatar class="size-[48px] bg-[#F2F2F2]" v-else/>
            <div class="flex-1 flex flex-col w-0">
              <div class="font-bold truncate">{{userStore.displayName}}</div>
              <div class="text-[#666666] text-[12px] truncate">{{userStore.profile.email}}</div>
            </div>
          </div>
          <div class="flex flex-col gap-[16px] leading-none">
            <RouterLink to="/me" class="flex items-center gap-[8px] cursor-pointer" @click="closeDropdown">
              <UserIcon class="size-[16px]" />
              <div class="text-[14px]">Profile</div>
            </RouterLink>
            <div class="flex items-center gap-[8px] cursor-pointer">
              <ArrowUpTrayIcon class="size-[16px] rotate-90" />
              <div class="text-[14px]" @click="logout">Sign out</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
  <div class="h-[64px]" />
</template>

<style scoped>
  #header {
    background: linear-gradient(90deg, rgba(184, 182, 216, 0.5) 0%, rgba(255, 255, 255, 0.5) 100%);
  }
</style>
