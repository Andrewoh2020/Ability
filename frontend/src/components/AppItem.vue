<script setup lang="ts">
import { ref, computed } from 'vue';
import { EllipsisVerticalIcon } from '@heroicons/vue/24/outline';
import { UserIcon } from '@heroicons/vue/24/solid';

import defaultAppIcon from '@/assets/app-icon.png';

import { App } from '@/types/app';
import { closeDropdown, formatTimeAgo } from '@/utils';
import { toast } from '@/utils/toast';
import { useBookmarkToggle, useDeleteApp } from '@/composables/app';
import { useModalStore } from '@/stores/modal';

import Modal from '@/components/Modal.vue';
import LoadingButton from '@/components/LoadingButton.vue';
import IconOrb from '@/components/IconOrb.vue';

const modalStore = useModalStore();

const props = defineProps<{
  data: App,
  type?: 'horizontal' | 'vertical' | 'simple',
  action?: boolean,
  collection?: boolean,
  closeModalOnNavigate?: boolean,
  customClass?: string
}>();

const emit = defineEmits<{
  'updated': [App];
  'deleted': [string];
}>();

const appCommunityUrl = `/apps/${props.data.id}/community`;
const userCommunityUrl = `/users/${props.data.creator?.id}/community`;

const handleNavigate = () => {
  if (props.closeModalOnNavigate) {
    modalStore.appList.show = false;
  }
};
const showDelete = ref(false);
const { mutate: deleteApp, isPending: loading } = useDeleteApp();
const { mutateAsync: bookmarkToggle, isPending: bookmarkToggleRunning } = useBookmarkToggle();

const appIcon = computed(() => {
  return props.data.icon ? props.data.icon : defaultAppIcon;
});

const appName = computed(() => {
  return props.data.name ? props.data.name : 'Untitled';
});

const destory = () => {
  deleteApp(props.data.id, {
    onSuccess: () => {
      showDelete.value = false;
      emit('deleted', props.data.id);
    }
  });
}

const showDeleteModal = () => {
  closeDropdown();
  showDelete.value = true;
}

const closeDeleteModal = () => {
  showDelete.value = false;
}

const copyLink = async () => {
  closeDropdown();
  const fullUrl = `${window.location.origin}${appCommunityUrl}`;
  try {
    await navigator.clipboard.writeText(fullUrl);
    toast.success('Link copied');
  } catch {
    toast.error('Failed to copy link');
  }
}

const removeFromCollection = async () => {
  if (bookmarkToggleRunning.value) return;
  closeDropdown();
  await bookmarkToggle(props.data.id);
  toast.success('Removed from Collection');
  emit('deleted', props.data.id);
}
</script>

<template>
  <div
    v-if="type === 'horizontal'"
    class="flex items-center gap-[16px]"
  >
    <RouterLink
      :to="appCommunityUrl"
      class="size-[60px] flex-shrink-0"
      @click="handleNavigate"
    >
      <IconOrb
        :url="appIcon"
        :name="appName"
      />
    </RouterLink>
    <div class="flex flex-col flex-1">
      <RouterLink
        :to="appCommunityUrl"
        class="text-[16px] md:text-[18px] font-semibold mb-[4px] truncate"
        @click="handleNavigate"
      >
        {{ appName }}
      </RouterLink>
      <div
        v-if="data.description"
        class="text-[#666666] text-[12px] mb-[2px] line-clamp-2"
      >
        {{ data.description }}
      </div>
      <div class="flex items-center">
        <RouterLink
          :to="userCommunityUrl"
          class="flex items-center gap-[2px]"
          @click="handleNavigate"
        >
          <img
            v-if="data.creator?.avatar_url"
            :src="data.creator.avatar_url"
            class="size-[16px] rounded-full"
          >
          <UserIcon
            v-else
            class="size-[16px] bg-white"
          />
          <div
            class="text-[#666666] text-[12px] capitalize"
          >
            {{ data.creator?.full_name || 'Anonymous' }}
          </div>
        </RouterLink>
        <span
          v-if="data.created_at"
          class="text-[#999999] text-[12px] ml-auto"
        >
          {{ formatTimeAgo(data.created_at) }}
        </span>
      </div>
    </div>
  </div>
  <div
    v-else-if="type === 'vertical'"
    class="relative flex flex-col justify-center items-center gap-[16px] w-[100%] h-[198px] px-[10px] pt-[30px] rounded-[16px] app-shadow"
    :class="customClass"
  >
    <RouterLink
      :to="appCommunityUrl"
      class="w-full max-w-[80px] flex-shrink-0"
      @click="handleNavigate"
    >
      <IconOrb
        :url="appIcon"
        :name="appName"
      />
    </RouterLink>
    <div class="flex flex-col gap-[4px] w-full">
      <RouterLink
        :to="appCommunityUrl"
        class="text-[18px] font-semibold text-center truncate"
        @click="handleNavigate"
      >
        {{ appName }}
      </RouterLink>
      <div class="h-[30px] text-[#666666] text-[12px] text-center line-clamp-2">
        {{ data.description }}
      </div>
    </div>
    <div
      v-if="action"
      class="absolute top-[8px] right-[8px] dropdown dropdown-end"
    >
      <div
        tabindex="0"
        role="button"
        class="cursor-pointer"
        @click="closeDeleteModal"
      >
        <EllipsisVerticalIcon class="size-[24px]" />
      </div>
      <div
        tabindex="0"
        class="flex flex-col w-[174px] p-[4px] rounded-[8px] bg-white shadow-md dropdown-content"
      >
        <RouterLink
          :to="`/projects/${data.id}`"
          class="p-[8px] cursor-pointer rounded-[4px] hover:bg-[#F2F2F2]"
          @click="handleNavigate"
        >
          Edit app
        </RouterLink>
        <div
          class="p-[8px] cursor-pointer rounded-[4px] hover:bg-[#F2F2F2]"
          @click="copyLink"
        >
          Share
        </div>
        <div
          class="p-[8px] cursor-pointer rounded-[4px] hover:bg-[#F2F2F2] text-red-500"
          @click="showDeleteModal"
        >
          Delete
        </div>
      </div>
    </div>
  </div>
  <div
    v-else-if="type === 'simple'"
    class="relative flex flex-col justify-center items-center gap-[16px] py-[10px] px-[5px] rounded-[16px] simple-item"
  >
    <RouterLink
      :to="appCommunityUrl"
      class="size-[70px]"
      @click="handleNavigate"
    >
      <IconOrb
        :url="appIcon"
        :name="appName"
      />
    </RouterLink>
    <RouterLink
      :to="appCommunityUrl"
      class="w-full"
      @click="handleNavigate"
    >
      <div class="w-full text-[14px] md:text-[18px] text-center truncate">
        {{ appName }}
      </div>
    </RouterLink>
    <div
      v-if="collection"
      class="absolute top-[8px] right-[8px] dropdown dropdown-end hidden"
    >
      <div
        tabindex="0"
        role="button"
        class="cursor-pointer"
        @click="closeDeleteModal"
      >
        <EllipsisVerticalIcon class="size-[24px]" />
      </div>
      <div
        tabindex="0"
        class="flex flex-col min-w-[174px] p-[4px] rounded-[8px] bg-white shadow-md dropdown-content"
      >
        <RouterLink
          v-if="data.type === 'owned'"
          :to="`/projects/${data.id}`"
          class="p-[8px] cursor-pointer rounded-[4px] hover:bg-[#F2F2F2]"
          @click="handleNavigate"
        >
          Edit app
        </RouterLink>
        <div
          class="p-[8px] cursor-pointer rounded-[4px] hover:bg-[#F2F2F2]"
          @click="copyLink"
        >
          Share
        </div>
        <div
          v-if="data.type === 'bookmarked'"
          class="p-[8px] text-red-500 cursor-pointer rounded-[4px] hover:bg-[#F2F2F2] whitespace-nowrap"
          @click="removeFromCollection"
        >
          Remove From Collection
        </div>
        <div
          v-else
          class="p-[8px] cursor-pointer rounded-[4px] hover:bg-[#F2F2F2] text-red-500"
          @click="showDeleteModal"
        >
          Delete
        </div>
      </div>
    </div>
  </div>
  <Modal
    v-if="showDelete"
    :show="true"
    type="prompt"
    @close="closeDeleteModal"
  >
    <div class="text-[20px] font-bold mb-[8px]">
      Permanently Delete?
    </div>
    <div class="text-[14px] mb-[8px]">
      <span class="font-bold">Warning:</span> This process is final. Once you confirm, the app and all of your data stored will be permanently deleted and cannot be restored.
    </div>
    <div class="text-[14px] p-[8px] mb-[16px] rounded-[8px] bg-[#F2F2F2]">
      <span class="font-bold">Note on Published Apps:</span> If this app is deleted, existing users will still retain the app and access to it. The app will only disappear from your list of apps.
    </div>
    <div class="flex justify-end gap-[16px]">
      <div
        class="cursor-pointer py-[10px] px-[16px]"
        @click="closeDeleteModal"
      >
        Cancel
      </div>
      <LoadingButton
        :loading="loading"
        class="text-white py-[10px] px-[16px] rounded-[40px] bg-[#EA3E3E]"
        @click="destory"
      >
        Delete
      </LoadingButton>
    </div>
  </Modal>
</template>

<style scoped>
  .dropdown {
    font-size: 14px;
  }
  .simple-item:hover {
    box-shadow: 0px 4px 60px 0px #0000000D;
    .dropdown {
      display: block;
    }
  }
</style>
