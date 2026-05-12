<script setup lang="ts">
import { ref, watch } from 'vue';
import { XMarkIcon } from '@heroicons/vue/24/outline';

import { closeDropdown } from '@/utils';

closeDropdown();

const typeClasses = {
  login: 'pt-[40px] px-[32px] pb-[32px] md:pt-[60px] md:px-[78px]',
  edit: 'p-[16px] md:p-[32px]',
  prompt: 'p-[32px]',
};

const emit = defineEmits<{
  'close': [];
}>();

const props = defineProps<{
  show: boolean,
  type: 'login' | 'edit' | 'prompt',
}>();

const modalShow = ref(props.show);
const isVisible = ref(false);

watch(() => props.show, (newValue) => {
  modalShow.value = newValue;
});

watch(() => modalShow.value, () => {
  changeVisible();
});

const changeVisible = () => {
  setTimeout(() => {
    isVisible.value = modalShow.value;
  }, 100);
}

const closeModal = () => {
  modalShow.value = false;
  setTimeout(() => {
    emit('close');
  }, 300);
}

changeVisible();

defineExpose({
  closeModal
});
</script>

<template>
  <dialog
    class="modal md:modal-middle"
    :class="{'modal-bottom': type != 'prompt', 'page-align': type == 'prompt'}"
    :open="isVisible"
  >
    <div
      class="
      relative w-full md:w-[540px] !max-w-none
      rounded-t-[16px] md:rounded-[16px]
      modal-box"
      :class="typeClasses[type]"
    >
      <XMarkIcon
        class="absolute top-[16px] right-[20px] size-[24px] text-[#999999] cursor-pointer"
        @click="closeModal"
      />
      <slot />
    </div>
  </dialog>
</template>

<style scoped>

</style>
