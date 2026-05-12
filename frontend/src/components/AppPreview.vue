<template>
  <div
    class="flex flex-col items-center w-full h-full bg-[#F7F3ED] preview-box"
    :class="[device, {full}]"
  >
    <div
      v-if="switchable"
      class="relative flex md:justify-center items-center gap-[24px] w-full py-4 px-[20px] md:px-0 bg-gray-700 text-white"
      :class="[allowBlack ? 'justify-between' : 'justify-center']"
    >
      <div
        v-if="allowBlack"
        class="md:absolute left-[20px] flex items-center gap-[4px] cursor-pointer"
        @click="routerBack"
      >
        <ArrowLeftIcon class="size-[16px]" />
        <div>Back</div>
      </div>
      <TvIcon
        class="hidden md:block device-icon"
        :class="{'active': device == 'pc'}"
        @click="device = 'pc'"
      />
      <DevicePhoneMobileIcon
        class="hidden md:block device-icon"
        :class="{'active': device == 'phone'}"
        @click="device = 'phone'"
      />
      <ArrowsPointingOutIcon
        v-if="!full"
        class="device-icon"
        @click="full = true"
      />
      <ArrowsPointingInIcon
        v-else
        class="device-icon"
        @click="full = false"
      />
    </div>
    <div
      ref="showcaseContainer"
      class="relative flex-1 flex justify-center items-center overflow-hidden showcase"
    >
      <div
        :class="device == 'phone' ? 'mockup-phone' : ''"
        :style="device == 'phone' ? phoneStyle : {}"
      >
        <div
          v-if="device == 'phone'"
          class="mockup-phone-camera"
        ></div>
        <div
          class="text-[#666666]"
          :class="device == 'phone' ? 'mockup-phone-display  grid place-content-center bg-[#F7F3ED]' : ''"
        >
          <div
            v-if="!init && isAppStageFetching"
            class="flex flex-col items-center justify-center h-full"
          >
            <img
              src="@/assets/building.gif"
              class="size-[164px] mb-[11px]"
            >
            <div class="text-[18px] text-center mb-[24px]">
              <div>Hang tight! We’re checking the app status.</div>
            </div>
          </div>
          <div
            v-else-if="appStage === AppStage.Default || appStage === AppStage.Building || appStage === AppStage.Planning"
            class="flex flex-col items-center justify-center h-full"
          >
            <img
              src="@/assets/building.gif"
              class="size-[164px] mb-[11px]"
            >
            <div class="text-[18px] text-center mb-[24px]">
              <div>Hang tight! We’re building the app.</div>
            </div>
          </div>
          <iframe
            v-else-if="publicUrl"
            :src="publicUrl"
            class="iframe"
            allow="camera; geolocation; microphone; autoplay; clipboard-write; picture-in-picture; popups; storage-access"
          ></iframe>
          <div
            v-else-if="isAppPreviewFetching"
            class="flex flex-col items-center justify-center h-full"
          >
            <img
              src="@/assets/building.gif"
              class="size-[164px] mb-[11px]"
            >
            <div class="max-w-[400px] text-[18px] text-center mb-[24px]">
              <div>Hang tight! We’re loading the app.</div>
            </div>
          </div>
          <div
            v-else-if="isAppPreviewError || isAppStageError"
            class="flex text-2xl text-center"
          >
            <div>Unexpected server error. Please try again later.</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, watchEffect, nextTick } from 'vue';
import {
  TvIcon, DevicePhoneMobileIcon, ArrowsPointingOutIcon, ArrowsPointingInIcon, ArrowLeftIcon,
} from '@heroicons/vue/24/outline';
import { AppStage } from '@/types/app';
import { useAppStage, useAppPreview } from '@/composables/app';
import { routerBack } from '@/utils';

const { appId, switchable } = defineProps({
  appId: {
    type: String,
    required: true,
  },
  allowBlack: {
    type: Boolean,
    default: false,
  },
  switchable: {
    type: Boolean,
    default: true,
  },
});

const ASPECT_RATIO = 375 / 750;
const device = ref('pc');
const full = ref(false);
const showcaseContainer = ref<HTMLDivElement | null>(null);
const phoneStyle = ref({});
const init = ref(false);

const {
  data: appStage,
  isError: isAppStageError,
  isFetching: isAppStageFetching,
} = useAppStage(appId, {
  retry: false,
  cacheTime: 0,
});

const {
  data: publicUrl,
  isError: isAppPreviewError,
  isFetching: isAppPreviewFetching,
} = useAppPreview(appId, {
  retry: false,
  cacheTime: 0,
});

const updatePhoneSize = () => {
  const container = showcaseContainer.value;
  if (!container) return

  const containerWidth = container.clientWidth - 20;
  const containerHeight = container.clientHeight - 20;

  const widthBasedHeight = containerWidth / ASPECT_RATIO;
  const heightBasedWidth = containerHeight * ASPECT_RATIO;

  let width = 0;
  let height = 0;
  if (widthBasedHeight <= containerHeight) {
    width = containerWidth;
    height = widthBasedHeight;
  } else {
    height = containerHeight;
    width = heightBasedWidth;
  }
  phoneStyle.value = {
    width: `${width}px`,
    height: `${height}px`
  }
};

watch(device, (newVal) => {
  if (newVal === 'phone') {
    nextTick(() => {
      setTimeout(updatePhoneSize, 100);
    });
  }
});

watchEffect(() => {
  if (appStage) {
    init.value = true;
  }
});

onMounted(() => {
  updatePhoneSize();
  window.addEventListener('resize', updatePhoneSize);
});

onUnmounted(() => {
  window.removeEventListener('resize', updatePhoneSize);
});
</script>

<style scoped>
.mockup-phone {
  position: relative;
  max-width: 375px;
  max-height: 750px;
  /* max-height: 100%; */
  /* aspect-ratio: 375 / 750; */
}

.preview-box {
  &.pc .showcase {
    width: 100%;
  }

  &.phone .showcase {
    max-width: 375px;
    width: 100%;
    border-radius: 32px;
  }

  &.full {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }
  .iframe {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100%;
  }
}

.device-icon {
  width: 32px;
  height: 32px;
  padding: 4px;
  cursor: pointer;
  border-radius: 8px;
  &.active {
    background-color: #FFFFFF26;
  }
}
</style>
