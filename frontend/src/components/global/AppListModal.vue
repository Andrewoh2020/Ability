<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import { XMarkIcon } from '@heroicons/vue/24/outline';

import { App } from '@/types/app';
import { useModalStore } from '@/stores/modal';
import { useGetMyApps, useGetAppsByMix } from '@/composables/app';

import AppItem from '@/components/AppItem.vue';
import AppItemSkeleton from '@/components/AppItemSkeleton.vue';

const props = defineProps<{
  type: 'mix' | 'public' | 'private',
  action?: boolean,
}>();

const showType = props.type === 'mix' ? 'simple' : 'vertical';
const lineNumberClass = {
  simple: 'grid-cols-4 md:grid-cols-6 xl:grid-cols-8',
  vertical: 'grid-cols-2 md:grid-cols-4 xl:grid-cols-7',
};

const modalStore = useModalStore();
const isVisible = ref(true);
const apps = ref<App[]>([]);
const hasMore = ref(true);
const options = reactive({
  page: 1,
  limit: 100,
  type: props.type,
  enabled: props.type !== 'mix'
});
const { data: listData, isFetching: loading } = useGetMyApps(options);
const mixOptions = reactive({
  page: 1,
  limit: 100,
});
const mixEnabled = computed(() => props.type === 'mix');
const { data: mixData, isFetching: mixLoading } = useGetAppsByMix(() => undefined, mixOptions, mixEnabled);

watch(listData, (newData) => {
  if (newData) {
    hasMore.value = newData.hasMore;
    apps.value = [...apps.value, ...newData.apps];
  }
}, {immediate: true});

watch(mixData, (newData) => {
  if (newData) {
    hasMore.value = newData.hasMore;
    apps.value = [...apps.value, ...newData.apps];
  }
}, {immediate: true});

const loadMore = (event) => {
  if (loading.value || mixLoading.value || !hasMore.value) return;

  const container = event.target;
  const scrollHeight = container.scrollHeight;
  const scrollTop = container.scrollTop;
  const clientHeight = container.clientHeight;

  if (scrollHeight - scrollTop - clientHeight <= 120) {
    if (props.type !== 'mix') {
      options.page++;
    } else {
      mixOptions.page++;
    }
  }
}

const closeModal = () => {
  isVisible.value = false;
  setTimeout(() => {
    modalStore.appList.show = false;
  }, 300);
}
</script>

<template>
  <dialog
    class="modal md:modal-middle"
    :open="isVisible"
  >
    <div class="flex flex-col gap-[10px] !w-[95%] !h-[95%] !max-w-[1550px] !max-h-[700px] !p-0 shadow-none bg-transparent modal-box overflow-visible">
      <XMarkIcon
        class="shrink-0 size-[24px] text-[#333333] ml-auto cursor-pointer"
        @click="closeModal"
      />
      <div
        class="flex-1 overflow-y-auto"
        @scroll="loadMore"
      >
        <div
          class="grid gap-[10px] md:gap-y-[28px] items-start py-[30px] md:pl-[75px] pr-[40px]"
          :class="[lineNumberClass[showType]]"
        >
          <template v-if="apps.length">
            <AppItem
              v-for="app in apps"
              :key="app.id"
              :data="app"
              :type="showType"
              :action="action"
              :collection="props.type === 'mix'"
              :close-modal-on-navigate="true"
            />
          </template>
          <template v-else-if="(loading || mixLoading) && !(apps.length)">
            <AppItemSkeleton
              v-for="_index in 10"
              :key="_index"
              :type="showType"
            />
          </template>
        </div>
      </div>
    </div>
  </dialog>
</template>

<style scoped>
  .modal {
    background: rgba(255, 255, 255, 0.95);
  }
</style>
