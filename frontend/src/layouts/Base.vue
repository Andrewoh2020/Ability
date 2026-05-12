<script setup lang="ts">
import Header from '@/components/Header.vue';
import Tabbar from '@/components/Tabbar.vue';
</script>

<template>
  <div class="main-bg-wrapper">
    <main class="flex flex-col min-h-[100vh] main-bg">
      <Header />
      <slot />
      <Tabbar />
    </main>
  </div>
</template>

<style scoped>
  .main-bg-wrapper {
    position: relative;
    background-size: 100% auto;
    background-repeat: no-repeat;
    background-image: url('@/assets/background.png');
  }
  .main-bg-wrapper::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    /* backdrop-filter: blur(40px);
    -webkit-backdrop-filter: blur(40px);
    pointer-events: none; */
  }
  .main-bg {
    position: relative;
  }
</style>
