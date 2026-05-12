<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';

import { CheckCircleIcon } from '@heroicons/vue/24/solid';


import { ToastOptions, closeToast } from '@/utils/toast';

const props = withDefaults(defineProps<ToastOptions>(), {
  timer: 3000,
  active: false,
});

const exiting = ref(false);

let timer: number;
onMounted(() => {
  timer = setTimeout(() => {
    exiting.value = true;
    setTimeout(closeToast, 300);
  }, props.timer);
});

onUnmounted(() => {
  clearTimeout(timer);
});

const alertClass = {
  'info': 'alert-info',
  'success': 'alert-success',
  'warning': 'alert-warning',
  'error': 'alert-error'
}[props.type];
</script>

<template>
  <div
    role="alert"
    class="fixed z-[2000] left-1/2 top-[20px] transform -translate-x-1/2 w-[fit-content] max-w-[300px] alert"
    :class="[alertClass, {out: exiting}]"
  >
    <svg
      v-if="props.type == 'info'"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      class="h-6 w-6 shrink-0 stroke-current"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
    <CheckCircleIcon
      v-else-if="props.type == 'success'"
      class="size-[24px]"
      :style="{ color: active ? '#75CD78' : 'white' }"
    />
    <svg
      v-else-if="props.type == 'warning'"
      xmlns="http://www.w3.org/2000/svg"
      fill="#FCB700"
      viewBox="0 0 24 24"
      class="h-6 w-6 shrink-0 stroke-current"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
      />
    </svg>
    <svg
      v-else-if="props.type == 'error'"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      class="h-6 w-6 shrink-0 stroke-current"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
    <span>{{ msg }}</span>
  </div>
</template>

<style scoped>
.alert {
  color: white;
  border: unset;
  padding: 8px;
  gap: 8px;
  background-color: #333333B2;
  border-radius: 40px;
  box-shadow: none;
  animation: slideDown 0.3s ease-out forwards;
}
.alert.out {
  animation: slideUp 0.3s ease-in forwards;
}

@keyframes slideDown {
  0% {
    transform: translateY(-100%);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}
@keyframes slideUp {
  0% {
    transform: translateY(0);
    opacity: 1;
  }
  100% {
    transform: translateY(-100%);
    opacity: 0;
  }
}
</style>
