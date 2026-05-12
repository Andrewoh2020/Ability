<script setup lang="ts">
import { ref } from 'vue';
import { ArrowUpTrayIcon, ArrowPathIcon } from '@heroicons/vue/24/outline';

import defaultIcon from '@/assets/app-icon.png';

import { toast } from '@/utils/toast';
import { useGenerateIcon, useUpdateApp } from '@/composables/app';
import { App, AppCategories } from '@/types/app';

import Modal from '@/components/Modal.vue';
import UploadImage from '@/components/UploadImage.vue';
import LoadingButton from '@/components/LoadingButton.vue';

const emit = defineEmits<{
  'updated': [App];
  'close': [];
}>();

const props = withDefaults(defineProps<{
  data: App,
  show?: boolean,
}>(), {
  show: true,
});

const editData = ref({ ...props.data });
const uploadRef = ref();
const { mutateAsync: updateApp, isPending: loading } = useUpdateApp();
const { mutateAsync: generateIcon, isPending: generateIconLoading } = useGenerateIcon();

const triggerUpload = () => {
  uploadRef.value.triggerFileSelect();
}

const uploadComplate = (url: string) => {
  editData.value.icon = url;
}

const save = async () => {
  if (!editData.value.name?.length) {
    toast.warning('Please enter the name');
    return;
  } else if (!editData.value.category) {
    toast.warning('Please select a category');
    return;
  }
  await updateApp(editData.value);
  emit('updated', editData.value);
}

const clickGenerateIcon = async () => {
  if (generateIconLoading.value) return;
  if (! editData.value.name) {
    toast.error('Please enter a name as a prompt');
    return;
  }
  const url = await generateIcon({
    id: editData.value.id,
    prompt: editData.value.name,
  });
  editData.value.icon = url;
}

const closeEditItemModal = () => {
  editData.value = { ...props.data };
  emit('close');
}
</script>

<template>
  <Modal
    :show="show"
    type="edit"
    @close="closeEditItemModal"
  >
    <div class="flex flex-col gap-[24px]">
      <div class="text-[20px] font-bold">
        Edit app details
      </div>
      <div class="flex flex-col gap-[12px]">
        <div class="flex justify-between items-center">
          <div class="text-[18px]">
            App name
          </div>
          <div class="text-[#666666] text-[14px]">
            {{ editData.name ? editData.name.length : 0 }}/20
          </div>
        </div>
        <input
          v-model="editData.name"
          type="text"
          class="w-full p-[16px] rounded-[40px] border-0 bg-[#F2F2F2] input"
          maxlength="20"
        >
      </div>
      <div class="flex flex-col gap-[12px]">
        <div class="flex justify-between items-center">
          <div class="text-[18px]">
            App description
          </div>
          <div class="text-[#666666] text-[14px]">
            {{ editData.description ? editData.description.length : 0 }}/255
          </div>
        </div>
        <textarea
          v-model="editData.description"
          class="w-full p-[16px] rounded-[24px] border-0 bg-[#F2F2F2] resize-none textarea"
          rows="2"
          maxlength="255"
        />
      </div>
      <div class="flex flex-col gap-[12px]">
        <div class="text-[18px]">
          App category
        </div>
        <select
          v-model="editData.category"
          class="w-full p-[16px] rounded-[40px] border-0 bg-[#F2F2F2] select"
        >
          <option value="null">
            Please select
          </option>
          <option
            v-for="(label, key) in AppCategories"
            :key="key"
            :value="key"
          >
            {{ label }}
          </option>
        </select>
      </div>
      <div class="flex flex-col gap-[12px]">
        <div class="text-[18px]">
          App icon
        </div>
        <div class="flex flex-col justify-center items-center gap-[16px] py-[32px] rounded-[24px] bg-[#F2F2F2]">
          <img
            :src="editData.icon ? editData.icon : defaultIcon"
            class="size-[64px] rounded-full"
          >
          <div class="max-w-[250px] text-[#666666] text-[14px] text-center">
            Upload image to change icon app or regenerate new icon
          </div>
          <div class="flex gap-[16px]">
            <UploadImage
              ref="uploadRef"
              @complete="uploadComplate"
            >
              <div
                class="flex items-center gap-[8px] py-[10px] px-[16px] cursor-pointer rounded-[40px] border-1 border-[#666666]"
                @click="triggerUpload"
              >
                <ArrowUpTrayIcon class="size-[16px]" />
                <div>Upload</div>
              </div>
            </UploadImage>
            <div
              class="flex items-center gap-[8px] py-[10px] px-[16px]  rounded-[40px] border-1 border-[#666666]"
              :class="[generateIconLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer']"
              @click="clickGenerateIcon"
            >
              <ArrowPathIcon
                class="size-[16px]"
                :class="{ 'animate-spin': generateIconLoading }"
              />
              <div>{{ generateIconLoading ? 'Generating...' : 'Generate icon' }}</div>
            </div>
          </div>
        </div>
      </div>
      <LoadingButton
        :loading="loading"
        class="text-white py-[14px] px-[16px] ml-auto rounded-[40px] btn-neutral"
        @click="save"
      >
        Save changes
      </LoadingButton>
    </div>
  </Modal>
</template>

<style scoped>

</style>
