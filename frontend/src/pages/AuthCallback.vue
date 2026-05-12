<script setup lang="ts">
import router from '@/router';
import { useUserStore } from '@/stores/user';

const hashParams = new URLSearchParams(window.location.hash.substring(1));
const accessToken = hashParams.get('access_token');
const refreshToken = hashParams.get('refresh_token');
if (accessToken && refreshToken) {
  window.history.replaceState(null, '', window.location.pathname + window.location.search);
  const userStore = useUserStore();
  userStore.login(accessToken, refreshToken);
}
router.push('/');
</script>

<template>
</template>

<style scoped>
</style>
