<script setup lang="ts">
import { ref, reactive, watch, computed, onMounted, onUnmounted } from 'vue';
import { ArrowRightIcon, ChevronDoubleDownIcon } from '@heroicons/vue/24/outline';

import { useUserStore } from '@/stores/user';
import { useModalStore } from '@/stores/modal';
import { AppCategory, AppCategories, App } from '@/types/app';
import { useHorizontalScroll } from '@/utils/useHorizontalScroll';
import { useGetAppsByMix, useGetAppsByCommunity, useGetAppsByFeatured } from '@/composables/app';

import AppItem from '@/components/AppItem.vue';
import AppItemSkeleton from '@/components/AppItemSkeleton.vue';

const modalStore = useModalStore();
const featuredScroll = useHorizontalScroll();
const categoriesScroll = useHorizontalScroll();
const communityAppsOptions = reactive({
  page: 1,
  category: '',
  size: 50,
});
const communityApps = ref<App[]>([]);
const communityHasMore = ref(true);
const { data: featuredApps, isFetching: featuredAppsLoading } = useGetAppsByFeatured();
const { data: communityData, isFetching: communityAppsLoading } = useGetAppsByCommunity(communityAppsOptions);
const showAllMyCollection = ref(false);
const userStore = useUserStore();
const isLogin = !!userStore.token;
const mixApps = ref<App[]>([]);
const { data: mixAppsData, isFetching: myAppsLoading } = useGetAppsByMix(
  () => undefined,
  {
    page: 1,
    limit: 35,
  },
  computed(() => isLogin),
);

watch(mixAppsData, (newData) => {
  if (newData) {
    mixApps.value = newData.apps;
  }
}, {immediate: true});

// Calculate columns per row based on screen size
const columnsPerRow = ref(4);

const updateColumnsPerRow = () => {
  const width = window.innerWidth;
  if (width >= 1280) {
    columnsPerRow.value = 9; // xl
  } else if (width >= 768) {
    columnsPerRow.value = 6; // md
  } else {
    columnsPerRow.value = 4; // default
  }
};

// Calculate the number of items that can be displayed in 2 rows
const twoRowsCount = computed(() => columnsPerRow.value * 2);

// Determine whether to show the expand button
const shouldShowChevron = computed(() => {
  if (!mixApps.value?.length) return false;
  return mixApps.value.length > twoRowsCount.value;
});

// Return items to display based on expand state
const displayedMyApps = computed(() => {
  if (!mixApps.value) return [];
  if (showAllMyCollection.value) return mixApps.value;
  return mixApps.value.slice(0, twoRowsCount.value);
});

const handleRemoveFromCollection = (appId: string) => {
  if (mixApps.value) {
    mixApps.value = mixApps.value.filter(app => app.id !== appId);
  }
};

watch(communityData, async (newData) => {
  if (newData) {
    communityHasMore.value = newData.hasMore;
    communityApps.value = [...communityApps.value, ...newData.apps];
  }
})

const myAppsIcons = computed(() => {
  const icons: string[] = [];
  if (mixApps.value?.length) {
    for (let index = mixApps.value.length - 1; index >= 0 && icons.length < 3; index--) {
      const app = mixApps.value[index]!;
      if (app.icon) {
        icons.unshift(app.icon);
      }
    }
  }
  return icons;
});

watch(featuredApps, (newData) => {
  if (newData) {
    featuredScroll.refresh();
  }
});

const changeCategory = (value: AppCategory | '') => {
  communityApps.value = [];
  communityHasMore.value = true;
  communityAppsOptions.page = 1;
  communityAppsOptions.category = value;
}

const handleScroll = () => {
  if (communityAppsLoading.value || !communityHasMore.value) return;

  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  const windowHeight = window.innerHeight;
  const documentHeight = document.documentElement.scrollHeight;

  if (documentHeight - scrollTop - windowHeight <= 120) {
    communityAppsOptions.page++;
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
  window.addEventListener('resize', updateColumnsPerRow);
  updateColumnsPerRow();
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('resize', updateColumnsPerRow);
});
</script>

<template>
  <div
    v-if="isLogin && (myAppsLoading || mixAppsData?.apps.length)"
    class="layout-content mb-[21px]"
  >
    <div class="flex justify-between items-center mb-[16px] md:mb-[24px]">
      <div class="text-[#3C518E] text-[20px] md:text-[24px] font-semibold">
        My Collection
      </div>
    </div>
    <div
      class="grid grid-cols-4 md:grid-cols-6 xl:grid-cols-9 gap-x-[10px] gap-y-[15px] xl:gap-x-[18px] xl:gap-y-[24px]"
    >
      <template v-if="displayedMyApps.length">
        <AppItem
          v-for="app in displayedMyApps"
          :key="app.id"
          :data="app"
          :collection="true"
          type="simple"
          @deleted="handleRemoveFromCollection"
        />
        <div
          v-if="mixAppsData?.hasMore && showAllMyCollection"
          class="flex flex-col justify-center items-center gap-[16px] cursor-pointer"
          @click="modalStore.openAppList('mix');"
        >
          <div
            v-if="myAppsIcons.length > 1"
            class="flex -space-x-[40px] justify-center"
          >
            <img
              v-for="(icon, index) in myAppsIcons.slice(0, 3)"
              :key="index"
              :src="icon"
              class="size-[70px] rounded-full"
            >
          </div>
          <img
            v-else
            src="@/assets/app-icon.png"
            class="size-[70px] rounded-full"
          >
          <div class="flex justify-center items-center gap-[4px]">
            <div class="text-[14px] md:text-[18px]">
              See All
            </div>
            <ArrowRightIcon class="size-[16px] md:size-[19px]" />
          </div>
        </div>
      </template>
      <template v-else-if="myAppsLoading && !(mixAppsData?.apps.length)">
        <AppItemSkeleton
          v-for="_index in 4"
          :key="_index"
          type="simple"
        />
      </template>
    </div>
    <ChevronDoubleDownIcon
      v-if="shouldShowChevron"
      class="size-[24px] cursor-pointer mx-auto mt-[16px]"
      :class="{
        'rotate-180': showAllMyCollection,
      }"
      @click="showAllMyCollection = !showAllMyCollection"
    />
  </div>
  <div class="flex-10 layout-content">
    <div
      v-if="featuredAppsLoading || featuredApps?.length"
      class="mb-[24px] md:mb-[32px]"
    >
      <div class="flex justify-between items-center mb-[16px] md:mb-[24px]">
        <div class="text-[#3C518E] text-[20px] md:text-[24px] font-semibold">
          Featured
        </div>
        <div
          v-if="featuredScroll.attr.canScroll"
          class="flex gap-[16px]"
        >
          <div
            v-if="featuredScroll.attr.position"
            class="flex justify-center items-center size-[28px] md:size-[32px] cursor-pointer bg-[#3C518E4D] rounded-full"
            @click="featuredScroll.scroll('left')"
          >
            <ArrowRightIcon class="text-[white] size-[16px] md:size-[19px] rotate-180" />
          </div>
          <div
            class="flex justify-center items-center size-[28px] md:size-[32px] cursor-pointer bg-[#3C518E4D] rounded-full"
            @click="featuredScroll.scroll('right')"
          >
            <ArrowRightIcon class="text-[white] size-[16px] md:size-[19px]" />
          </div>
        </div>
      </div>
      <div
        :ref="featuredScroll.container"
        class="flex gap-[16px] overflow-x-auto scrollbar-hide app-box-shadow"
      >
        <template v-if="featuredApps?.length">
          <AppItem
            v-for="app in featuredApps"
            :key="app.id"
            custom-class="!w-[160px] flex-shrink-0"
            :data="app"
            type="vertical"
          />
        </template>
        <template v-else-if="featuredAppsLoading && !(featuredApps?.length)">
          <AppItemSkeleton
            v-for="_index in 4"
            :key="_index"
            type="vertical"
            class="w-[160px] flex-shrink-0 app-shadow"
          />
        </template>
      </div>
    </div>
    <div>
      <div class="flex justify-between items-center mb-[16px] md:mb-[24px]">
        <div class="text-[#3C518E] text-[20px] md:text-[24px] font-semibold">
          Community
        </div>
        <div
          v-if="categoriesScroll.attr.canScroll"
          class="flex gap-[16px]"
        >
          <div
            v-if="categoriesScroll.attr.position"
            class="flex justify-center items-center size-[28px] md:size-[32px] cursor-pointer bg-[#3C518E4D] rounded-full"
            @click="categoriesScroll.scroll('left')"
          >
            <ArrowRightIcon class="text-[white] size-[16px] md:size-[19px] rotate-180" />
          </div>
          <div
            class="flex justify-center items-center size-[28px] md:size-[32px] cursor-pointer bg-[#3C518E4D] rounded-full"
            @click="categoriesScroll.scroll('right')"
          >
            <ArrowRightIcon class="text-[white] size-[16px] md:size-[19px]" />
          </div>
        </div>
      </div>
      <div
        :ref="categoriesScroll.container"
        class="flex items-center gap-[12px] mb-[16px] md:mb-[24px] overflow-x-auto scrollbar-hide"
      >
        <div
          :class="communityAppsOptions.category === '' ? 'category-active' : ''"
          class="h-[40px] text-[14px] font-bold cursor-pointer leading-[40px] px-[12px] md:px-[24px] rounded-[20px] bg-[#0000000D] whitespace-nowrap"
          @click="changeCategory('')"
        >
          Recent
        </div>
        <div
          v-for="(name, key) in AppCategories"
          :key="key"
          :class="communityAppsOptions.category === key ? 'category-active' : ''"
          class="h-[40px] text-[14px] cursor-pointer leading-[40px] px-[12px] md:px-[24px] rounded-[20px] bg-[#0000000D] whitespace-nowrap"
          @click="changeCategory(key)"
        >
          {{ name }}
        </div>
      </div>
      <div class="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-y-[12px] gap-x-[24px]">
        <template v-if="communityApps?.length">
          <AppItem
            v-for="app in communityApps"
            :key="app.id"
            :data="app"
            type="horizontal"
          />
        </template>
        <template v-else-if="communityAppsLoading && !(communityApps?.length)">
          <AppItemSkeleton
            v-for="_index in 4"
            :key="_index"
            type="horizontal"
          />
        </template>
      </div>
      <div
        v-if="communityAppsLoading && communityApps?.length"
        class="text-center py-[24px]"
      >
        <span class="text-[#999] text-[14px]">Loading...</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .category-active {
    color: white;
    background: linear-gradient(90deg, rgba(99, 70, 143, 0.8) 0%, rgba(61, 82, 142, 0.8) 51.44%, rgba(61, 82, 142, 0.8) 91.83%);
  }
</style>
