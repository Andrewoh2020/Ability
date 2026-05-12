<script setup lang="ts">
withDefaults(defineProps<{
  show?: boolean,
}>(), {
  show: true,
});
</script>

<template>
  <div class="rounded skeleton" v-if="show"></div>
  <slot v-else></slot>
</template>

<style scoped>

</style>
