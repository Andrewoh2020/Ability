<script setup lang="ts">
defineProps<{
  type?: 'horizontal' | 'vertical' | 'simple'
}>();

</script>

<template>
  <div
    v-if="type === 'horizontal'"
    class="flex items-center gap-[16px]"
  >
    <img
      src="@/assets/app-skeleton-icon.png"
      class="size-[60px] rounded-full"
    >
    <img
      src="@/assets/app-skeleton-texts.png"
      class="flex-1 h-[42px]"
    >
  </div>
  <div
    v-else-if="type === 'vertical'"
    class="flex flex-col justify-center items-center gap-[16px] w-[100%] h-[198px] px-[10px] rounded-[16px]"
  >
    <img
      src="@/assets/app-skeleton-icon.png"
      class="size-[80px] rounded-full"
    >
    <img
      src="@/assets/app-skeleton-texts-center.png"
      class="w-full"
    >
  </div>
  <div
    v-else-if="type === 'simple'"
    class="flex flex-col justify-center items-center gap-[16px]"
  >
    <img
      src="@/assets/app-skeleton-icon.png"
      class="size-[70px] md:size-[75px] rounded-full"
    >
    <img
      src="@/assets/app-skeleton-text.png"
      class="w-full"
    >
  </div>
</template>

<style scoped>

</style>
