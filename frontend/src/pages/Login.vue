<script setup lang="ts">
import router from '@/router';

import Logo from '@/components/Logo.vue';
import Login from '@/components/Login.vue';

const handleLogined = () => {
  router.push('/');
}
</script>

<template>
  <div class="flex-1 flex">
    <div class="flex-1 relative hidden md:flex flex-col justify-center items-center background">
      <div class="px-[50px] lg:px-[79px]">
        <RouterLink to="/">
          <Logo class="absolute top-[20px] left-0 page-align"/>
        </RouterLink>
        <div class="text-white text-[48px] font-bold text-center">Build Anything, To Do Everything</div>
      </div>
    </div>
    <div class="flex-1 relative flex flex-col justify-center items-center background md:!bg-[image:none]">
      <RouterLink to="/" class="md:hidden">
        <Logo class="absolute top-[20px] left-0 page-align"/>
      </RouterLink>
      <div class="w-full max-w-[400px] page-align">
        <Login @logined="handleLogined"/>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .background {
    background-position: 0 0;
    background-size: cover 118.6%;
    background-repeat: no-repeat;
    background-image: url(@/assets/background.png);
  }
</style>
