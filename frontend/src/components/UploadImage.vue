<script setup lang="ts">
import { ref } from 'vue';
import Compressor from 'compressorjs';

import { toast } from '@/utils/toast';
import { useUploadImage } from '@/composables/tool';

const props = withDefaults(defineProps<{
  maxSize?: number,
}>(), {
  maxSize: 5,
});

const emit = defineEmits<{
  'complete': [string];
}>();

const loading = ref(false);
const fileInput = ref<HTMLInputElement>();

const { mutateAsync: uploadImage } = useUploadImage();

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    toast.info('Please select an image file');
    return;
  }
  if (file.size > props.maxSize * 1024 * 1024) {
    toast.warning(`Image size should be less than ${props.maxSize}MB`);
    return;
  }
  loading.value = true;
  try {
    const formData = new FormData();
    const compressedFile = await new Promise((resolve, reject) => {
      new Compressor(file, {
        quality: 0.8,
        maxWidth: 512,
        maxHeight: 512,
        mimeType: 'image/webp',
        success: resolve,
        error: reject,
      });
    }) as Blob;
    formData.append('file', compressedFile, 'image.webp');
    const url = await uploadImage({formData, onProgress: null});
    emit('complete', url);
  } catch (_) {
    toast.error('Upload failed, please try again');
  } finally {
    loading.value = false;
    if (target) target.value = '';
  }
}

defineExpose({
  triggerFileSelect: () => {
    fileInput.value?.click();
  }
});
</script>

<template>
  <slot />
  <input
    ref="fileInput"
    type="file"
    accept="image/*"
    class="!hidden"
    @change="handleFileSelect"
  >
</template>

<style scoped>

</style>
