<script setup lang="ts">
import { onUnmounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ChatBubbleOvalLeftIcon, ArrowLeftIcon, PlusCircleIcon } from '@heroicons/vue/24/solid';

import { closeDropdown, routerBack } from '@/utils';
import { toast } from '@/utils/toast';
import { useUserStore } from '@/stores/user';
import { AppCommunityDetail } from '@/types/app';
import { useGetAppCommunityDetail, useBookmarkToggle } from '@/composables/app';

import AppPreview from '@/components/AppPreview.vue';
import AppComments from '@/components/AppComments.vue';
import IconOrb from '@/components/IconOrb.vue';
import { resetPageDescription, resetPageTitle, setPageDescription, setPageTitle } from '@/utils/pageMeta';


const route = useRoute();
const appId = route.params.id as string;
const app = ref<AppCommunityDetail>();
const { data: appData } = useGetAppCommunityDetail(appId);
const { mutateAsync: bookmarkToggle, isPending: bookmarkToggleRunning } = useBookmarkToggle();
const showCommentsModal = ref(false);
const userStore = useUserStore();

watch(appData, (newData) => {
  if (newData) {
    app.value = {...newData};
    if (app.value.name) {
      setPageTitle(app.value.name);
    }
    if (app.value.description) {
      setPageDescription(app.value.description);
    }
  }
})

const likeChange = (value) => {
  app.value!.likes_count += value;
}

const followerChange = (value) => {
  app.value!.creator.followers_count += value;
}

const clickBookmarkToggle = async () => {
  if (!app.value || bookmarkToggleRunning.value) return;
  await bookmarkToggle(app.value.id);
  app.value.has_bookmark = !app.value.has_bookmark;
  app.value.bookmarks_count += app.value.has_bookmark ? 1 : -1;
  if (app.value.has_bookmark) {
    toast.success('Added to Collection', { active: true });
  } else {
    toast.success('Removed from Collection');
  }
}

const copyLink = async () => {
  closeDropdown();
  const fullUrl = `${window.location.origin}/apps/${app.value?.id}/community`;
  try {
    await navigator.clipboard.writeText(fullUrl);
    toast.success('Link copied');
  } catch {
    toast.error('Failed to copy link');
  }
}

onUnmounted(() => {
  resetPageTitle();
  resetPageDescription();
})
</script>

<template>
  <main class="flex flex-col h-full main-bg">
    <div class="flex-shrink-0 relative flex justify-between h-[60px] md:h-[88px] py-[14px] md:py-[18px] page-align header">
      <div
        class="flex items-center gap-[4px] cursor-pointer"
        @click="routerBack"
      >
        <ArrowLeftIcon class="size-[24px] " />
        <span class="text-[20px]">Back</span>
      </div>
      <div
        v-if="app?.icon"
        class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 size-[48px] md:size-[72px]"
      >
        <IconOrb
          :url="app.icon"
        />
      </div>
      <img
        v-else-if="app"
        src="@/assets/app-icon.png"
        class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 size-[48px] md:size-[72px] rounded-full"
      >
      <div
        v-if="app"
        class="flex items-center gap-[10px] md:gap-[16px]"
      >
        <div
          v-if="app.creator.id != userStore.profile?.id"
          class="flex justify-center items-center gap-[8px] size-[32px] md:size-auto md:p-[14px] cursor-pointer rounded-full md:rounded-[40px] bg-[#333333]"
          @click="clickBookmarkToggle"
        >
          <PlusCircleIcon class="text-white size-[16px] md:size-[24px]" />
          <div class="hidden xl:inline-block text-white">
            {{ app.has_bookmark ? 'Added' : 'Add to Collection' }}
          </div>
        </div>
        <div
          class="flex justify-center items-center gap-[8px] size-[32px] md:size-auto md:p-[14px] cursor-pointer rounded-full md:rounded-[40px] bg-[#333333]"
          @click="showCommentsModal = true"
        >
          <ChatBubbleOvalLeftIcon class="text-white size-[16px] md:size-[24px]" />
          <div class="hidden xl:inline-block text-white">
            Comment
          </div>
        </div>
        <div
          class="flex justify-center items-center gap-[8px] size-[32px] md:size-auto md:p-[14px] cursor-pointer rounded-full md:rounded-[40px] bg-[#333333]"
          @click="copyLink"
        >
          <img
            src="@/assets/share-icon.svg"
            class="size-[16px] md:size-[24px]"
          >
          <div class="hidden xl:inline-block text-white">
            Share
          </div>
        </div>
      </div>
    </div>
    <AppPreview
      :app-id="appId"
      :allow-black="true"
      :switchable="false"
    />
  </main>
  <AppComments
    v-if="showCommentsModal && app"
    :app="app"
    :show="true"
    @close="showCommentsModal = false"
    @like-change="likeChange"
    @click-bookmark="clickBookmarkToggle"
    @follower-change="followerChange"
  />
</template>

<style scoped>
  .header {
    background-color: white;
  }
</style>
