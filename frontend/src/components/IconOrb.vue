<script setup lang="ts">
defineProps<{
  url: string,
  name?: string,
}>();
</script>

<template>
  <div class="relative aspect-square rounded-full">
    <img
      :src="url"
      :alt="name"
      class="size-full rounded-full"
    >
    <img
      src="@/assets/light-shadow.png"
      class="absolute -top-[7px] -left-[7px] w-full"
    >
  </div>
</template>

<style scoped>

</style>
