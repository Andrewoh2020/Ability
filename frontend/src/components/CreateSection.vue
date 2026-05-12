<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { ArrowUpRightIcon, XMarkIcon } from '@heroicons/vue/24/outline';

import router from '@/router';
import { useModalStore } from '@/stores/modal';
import { useCreateApp } from '@/composables/app';

import LoadingButton from '@/components/LoadingButton.vue';

const emit = defineEmits<{
  'close': [];
}>();

const props = defineProps<{
  show: boolean,
}>();
const modalStore = useModalStore();
const modalShow = ref(props.show);
const isVisible = ref(false);
const question = ref('');
const { mutateAsync: createApp, isPending: loading } = useCreateApp();
const textareaRef = ref<HTMLTextAreaElement>();
const displayPlaceholder = ref('');
const typingExamples = [
  'track my expenses Webpages',
  'turn HEIC photos into JPEG Webpages',
  'track my ovulation cycle Webpages',
  'help my friends find times to hangout on my calendar Webpages',
  'help me learn more Japanese vocabulary Webpages',
  'make passport-friendly photos Webpages',
];

watch(() => props.show, (newValue) => {
  modalShow.value = newValue;
});

watch(modalShow, (newValue) => {
  changeVisible();
  if (newValue) {
    startTypingEffect();
  } else {
    stopTypingEffect();
  }
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
    modalStore.showCreateSection = false;
  }, 300);
}

const updateTextareaHeight = async () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = '60px';
    textareaRef.value.style.overflowY = 'hidden';
    const newHeight = Math.max(textareaRef.value.scrollHeight, 60);
    textareaRef.value.style.height = newHeight + 'px';
    textareaRef.value.style.overflowY = 'auto';
  }
}

const handleEnter = (event) => {
  if (event.ctrlKey || event.metaKey || event.shiftKey) {
    return;
  } else {
    event.preventDefault();
    submit();
  }
}

const submit = async () => {
  if (!question.value.trim()) return;
  const id = await createApp();
  modalStore.showCreateSection = false;
  router.push({
    path: `/projects/${id}`,
    query: {
      initQuestion: question.value
    }
  });
}

let currentExampleIndex = 0;
let currentCharIndex = 0;
let isDeleting = false;
let typingTimer;
const startTypingEffect = () => {
  clearInterval(typingTimer);
  typingTimer = setInterval(() => {
    const currentExample = typingExamples[currentExampleIndex]!;
    // Distinguish whether to delete or add
    if (!isDeleting) {
      // Set the current sentence to delete status after completion
      if (currentCharIndex < currentExample.length) {
        displayPlaceholder.value = currentExample.substring(0, currentCharIndex + 1);
        currentCharIndex++;
      } else {
        isDeleting = true;
        clearInterval(typingTimer);
        setTimeout(startTypingEffect, 1000);
      }
    } else {
      // Reset to new status after deletion is complete
      if (currentCharIndex > 0) {
        displayPlaceholder.value = currentExample.substring(0, currentCharIndex - 1);
        currentCharIndex--;
      } else {
        isDeleting = false;
        currentExampleIndex = (currentExampleIndex + 1) % typingExamples.length;
        currentCharIndex = 0;
        displayPlaceholder.value = '';
        clearInterval(typingTimer);
        startTypingEffect();
      }
    }
  }, 60);
}

const stopTypingEffect = () => {
  if (typingTimer) {
    clearInterval(typingTimer);
    typingTimer = null;
  }
};

onMounted(() => {
  changeVisible();
  startTypingEffect();
});

onUnmounted(() => {
  clearInterval(typingTimer);
});
</script>

<template>
  <dialog
    class="modal modal-bottom md:modal-middle"
    :open="isVisible"
  >
    <div class="relative flex flex-col items-center lg:w-[790px] !max-w-none px-[20px] md:p-[40px] bg-white/30 rounded-t-[40px] md:rounded-[40px] backdrop-blur-[10px] modal-box">
      <XMarkIcon
        class="absolute top-[24px] right-[24px] size-[24px] text-white cursor-pointer"
        @click="closeModal"
      />
      <div class="text-white text-[30px] md:text-[48px] text-center px-[10%] mb-[12px]">
        Build Anything, To Do Everything
      </div>
      <div class="text-white text-[16px] md:text-[20px] text-center mb-[20px] md:mb-[40px]">
        Tell us what app you want and we'll build it.
      </div>
      <div class="flex items-center w-full max-w-[640px] bg-white rounded-[40px]">
        <textarea
          ref="textareaRef"
          v-model="question"
          :disabled="loading"
          class="w-full h-[60px] max-h-[250px] text-[14px] md:text-[18px] leading-[20px] px-[18px] md:px-[24px] py-[20px] rounded-[40px] border-none resize-none inputDom"
          maxlength="1000"
          :placeholder="`Build an app that can ${displayPlaceholder}`"
          @input="updateTextareaHeight"
          @keydown.enter="handleEnter"
        />
        <div class="flex justify-end w-[50px] pr-[10px] mt-auto mb-[10px] actions">
          <LoadingButton
            :loading="loading"
            :replace="true"
            class="w-[40px] h-[40px] p-0 rounded-full btn btn-neutral"
            :disable="!question.trim()"
            @click="submit"
          >
            <ArrowUpRightIcon class="size-[20px] text-white" />
          </LoadingButton>
        </div>
      </div>
    </div>
    <div
      class="modal-backdrop"
      @click="closeModal"
    />
  </dialog>
</template>

<style scoped>
  .inputDom::placeholder {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
