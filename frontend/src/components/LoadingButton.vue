<script setup lang="ts">
defineProps<{
  loading: boolean,
  disable?: boolean,
  replace?: boolean,
}>();
</script>

<template>
  <button class="btn" :disabled="disable || loading">
    <span class="loading loading-spinner" v-if="loading"></span>
    <slot v-if="!replace || !loading"></slot>
  </button>
</template>

<style scoped>

</style>
