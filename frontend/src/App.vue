<script setup lang="ts">
import { watch } from 'vue';

import { useUserStore } from './stores/user';
import { useModalStore } from '@/stores/modal';

import CreateSection from '@/components/CreateSection.vue';
import LoginModal from '@/components/global/LoginModal.vue';
import EditProfileModal from '@/components/global/EditProfileModal.vue';
import AppListModal from '@/components/global/AppListModal.vue';
import { useGetUserProfile } from './composables/user';

const userStore = useUserStore();
const modalStore = useModalStore();

const {data: profile} = useGetUserProfile(!!userStore.token && !userStore.profile);

watch(profile, (newProfile) => {
  userStore.profile = newProfile!;
});
</script>

<template>
  <RouterView />
  <LoginModal v-if="modalStore.showLogin" />
  <EditProfileModal v-if="modalStore.showEditProfile" />
  <CreateSection v-if="modalStore.showCreateSection" :show="true"/>
  <AppListModal v-if="modalStore.appList.show" :type="modalStore.appList.type" :action="modalStore.appList.action"/>
</template>

<style>
</style>
