<template>
  <header class="flex flex-col md:flex-row md:items-center gap-[16px] md:gap-[10px] py-[8px] md:py-[16px] shadow-sm page-align">
    <div class="flex items-center gap-[16px]">
      <ArrowLeftIcon
        class="flex-shrink-0 size-[24px] cursor-pointer"
        @click="routerBack"
      />
      <Skeleton
        class="size-[32px] md:size-[48px]"
        :show="loading"
      >
        <img
          :src="app && app.icon ? app.icon : defaultIcon"
          class="size-[32px] md:size-[48px] rounded-[10px]"
        >
      </Skeleton>
      <div class="flex-1 flex flex-row md:flex-col justify-between md:justify-center items-start gap-[4px]">
        <div class="flex items-center gap-[4px]">
          <Skeleton
            class="w-[100px] h-[22.5px]"
            :show="loading"
          >
            <div
              v-if="app"
              class="max-w-[120px] text-[18px] font-bold truncate"
            >
              {{ app.name ? app.name : 'Untitled' }}
            </div>
          </Skeleton>
          <PencilSquareIcon
            v-if="app"
            class="size-[16px] cursor-pointer"
            @click="showEditItemModal"
          />
        </div>
        <Skeleton
          class="w-[70px] h-[19.5px]"
          :show="loading"
        >
          <div
            v-if="app && app.category"
            class="text-[12px] px-[8px] py-[3.5px] rounded-[20px] bg-[#F2F2F2]"
          >
            {{ AppCategories[app.category] }}
          </div>
        </Skeleton>
      </div>
    </div>
  </header>
  <main class="relative flex-1 flex overflow-hidden">
    <div class="flex-1 md:flex-none flex flex-col md:w-[400px] p-[16px]">
      <div class="flex items-center gap-[8px] pb-[16px]">
        <div class="flex justify-center items-center size-[32px] ball">
          <img
            src="@/assets/logo.svg"
            class="size-[16px]"
          >
        </div>
        <div class="flex flex-col gap-[2px] h-[32px]">
          <div class="text-[16px] font-bold">
            Ability
          </div>
          <div
            v-if="app"
            class="text-[12px]"
          >
            Last updated {{ formatDate(app.updated_at) }}
          </div>
        </div>
      </div>
      <div
        ref="messagesContainer"
        class="flex-1 flex flex-col gap-[18px] pb-[18px] overflow-y-scroll scrollbar-hide"
        @scroll="handleScroll"
      >
        <div
          v-if="loadingEventsData"
          class="flex w-full flex-col gap-4"
        >
          <div class="skeleton h-4 w-50 self-end" />
          <div class="skeleton h-4 w-full" />
          <div class="skeleton h-4 w-full" />
          <div class="skeleton h-4 w-full" />
          <div class="skeleton h-4 w-full" />
          <div class="skeleton h-4 w-full" />
          <div class="skeleton h-4 w-full" />
          <div class="skeleton h-4 w-full" />
          <div class="skeleton h-4 w-full" />
          <div class="skeleton h-4 w-full" />
        </div>
        <template
          v-for="(message, index) in messages"
          :key="message.id"
        >
          <template v-if="message.type === 'error'">
            <div role="alert" class="alert alert-error alert-outline">
              {{ message.data }}
            </div>
          </template>
          <template v-else-if="message.type === 'message'">
            <div
              v-if="message.role == 'user'"
              class="self-end max-w-[80%] text-[14px] leading-[20px] p-[8px] bg-[#F2F2F2] rounded-[8px]"
            >
              {{ message.data }}
            </div>
            <div
              v-else
              class="self-start w-full text-[14px] leading-[20px]"
              v-html="message.htmlContent"
            ></div>
          </template>
          <template v-else-if="message.type === 'progress'">
            <div class="w-full p-[16px] rounded-[16px] bg-white plan-card-shadow">
              <div class="flex flex-col items-center mb-[16px]">
                <div class="relative w-[80px] h-[80px] mb-[12px]">
                  <svg
                    class="absolute inset-0 w-full h-full"
                    viewBox="0 0 80 80"
                    style="transform: rotate(-90deg);"
                  >
                    <circle
                      cx="40"
                      cy="40"
                      r="37"
                      fill="none"
                      stroke="#E5E7EB"
                      stroke-width="5"
                    />
                    <circle
                      cx="40"
                      cy="40"
                      r="37"
                      fill="none"
                      stroke="url(#progressGradient)"
                      stroke-width="5"
                      stroke-linecap="round"
                      :stroke-dasharray="`${getProgressPercentage(message.data) * 2.32} 232`"
                    />
                    <defs>
                      <linearGradient
                        id="progressGradient"
                        x1="0%"
                        y1="0%"
                        x2="100%"
                        y2="0%"
                      >
                        <stop
                          offset="0%"
                          stop-color="#C097FC"
                        />
                        <stop
                          offset="50%"
                          stop-color="#668AF1"
                        />
                        <stop
                          offset="100%"
                          stop-color="#6EDFFA"
                        />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div class="absolute inset-[10px] rounded-full overflow-hidden bg-white">
                    <img
                      v-if="app?.icon"
                      :src="app.icon"
                      class="w-full h-full rounded-full object-cover"
                    >
                    <div
                      v-else
                      class="w-full h-full rounded-full bg-gray-200"
                    />
                  </div>
                </div>
                <div class="flex justify-between items-baseline w-full">
                  <div class="text-[18px] font-bold">
                    {{ app?.name }}
                  </div>
                  <div
                    v-if="getProgressPercentage(message.data) < 100"
                    class="text-[14px] text-gray-500 text-right"
                  >
                    Estimated time {{ message.data.length }} minutes
                  </div>
                  <div
                    v-else
                    class="text-[14px] text-gray-500 text-right"
                  >
                    Completed
                  </div>
                </div>
              </div>
              <div class="p-[12px] rounded-[8px] border border-gray-100">
                <div class="relative">
                  <div class="absolute left-[10px] top-[24px] bottom-[24px] w-[4px] bg-gray-200 z-0" />
                  <div class="space-y-[8px]">
                    <div
                      v-for="(item, idx) in message.data"
                      :key="idx"
                      class="flex items-center gap-[12px] relative"
                    >
                      <div class="flex items-center justify-center w-[24px] h-[24px] bg-white">
                        <div
                          v-if="item.status === 'completed'"
                          class="flex items-center justify-center w-[20px] h-[20px] rounded-full bg-[#1F2937]"
                        >
                          <CheckIcon class="w-[12px] h-[12px] text-white" />
                        </div>
                        <div
                          v-else-if="item.status === 'in_progress'"
                          class="w-[20px] h-[20px]"
                        >
                          <svg
                            class="animate-spin"
                            viewBox="0 0 24 24"
                            fill="none"
                          >
                            <circle
                              class="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              stroke-width="3"
                            />
                            <path
                              class="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                          </svg>
                        </div>
                        <div
                          v-else
                          class="w-[20px] h-[20px] rounded-full border-2 border-gray-300 bg-white"
                        />
                      </div>
                      <span
                        class="text-[14px]"
                        :class="{
                          'text-gray-900': item.status === 'completed',
                          'text-gray-700 font-medium': item.status === 'in_progress',
                          'text-gray-400': item.status === 'pending'
                        }"
                      >
                        {{ item.content }}
                      </span>
                    </div>
                  </div>
                </div>

                <template v-if="index === messages.length - 1">
                  <!-- Error state -->
                  <div
                    v-if="planError"
                    class="flex items-center gap-[12px] mt-[16px]"
                  >
                    <div class="flex items-center justify-center w-[24px] h-[24px] flex-shrink-0 rounded-full bg-red-500">
                      <XCircleIcon class="w-[14px] h-[14px] text-white" />
                    </div>
                    <span class="text-[14px] leading-[20px]">App failed to be created.</span>
                  </div>
                  <!-- Completed state -->
                  <div
                    v-else-if="getProgressPercentage(message.data) === 100"
                    class="flex items-center gap-[12px] mt-[16px]"
                  >
                    <div class="flex items-center justify-center w-[24px] h-[24px] flex-shrink-0 rounded-full bg-green-500">
                      <CheckIcon class="w-[14px] h-[14px] text-white" />
                    </div>
                    <span class="text-[14px] leading-[20px]">Done! Your app is up and running. Give it a moment to load.</span>
                  </div>
                </template>
              </div>
            </div>
          </template>
        </template>

        <!-- Preparing state with new request -->
        <div
          v-if="buildStatus === 'preparing' && !planData"
          class="flex items-start gap-[8px] w-full"
        >
          <div class="flex items-center justify-center w-[24px] h-[20px]">
            <span class="typing-dots text-[#668AF1]">...</span>
          </div>
          <span class="text-[14px] leading-[20px]">Got it, taking some time to understand your request…</span>
        </div>
        <!-- Skeleton loading for planning card -->
        <div
          v-else-if="planLoading && !planData"
          class="w-full p-[16px] rounded-[16px] bg-white plan-card-shadow animate-pulse"
        >
          <div class="flex flex-col items-center mb-[16px]">
            <div class="w-[80px] h-[80px] rounded-full bg-gray-200 mb-[12px]" />
            <div class="flex justify-between w-full">
              <div class="w-[120px] h-[20px] bg-gray-200 rounded" />
              <div class="w-[100px] h-[20px] bg-gray-200 rounded" />
            </div>
          </div>
          <div class="flex items-start gap-[8px] mb-[12px]">
            <div class="w-[24px] h-[20px] bg-gray-200 rounded" />
            <div class="flex-1 h-[40px] bg-gray-200 rounded" />
          </div>
          <div class="p-[12px] rounded-[8px] border border-gray-100">
            <div class="space-y-[12px]">
              <div class="flex items-center gap-[8px]">
                <div class="w-[20px] h-[20px] bg-gray-200 rounded" />
                <div class="flex-1 h-[20px] bg-gray-200 rounded" />
              </div>
              <div class="flex items-center gap-[8px]">
                <div class="w-[20px] h-[20px] bg-gray-200 rounded" />
                <div class="flex-1 h-[20px] bg-gray-200 rounded" />
              </div>
              <div class="flex items-center gap-[8px]">
                <div class="w-[20px] h-[20px] bg-gray-200 rounded" />
                <div class="flex-1 h-[20px] bg-gray-200 rounded" />
              </div>
            </div>
          </div>
        </div>
        <!-- Features Planning Card -->
        <div
          v-else-if="planData"
          class="w-full p-[16px] rounded-[16px] bg-white plan-card-shadow"
        >
          <!-- Project icon and header -->
          <div class="flex flex-col items-center mb-[16px]">
            <div class="relative w-[80px] h-[80px] mb-[12px]">
              <!-- App icon -->
              <div class="absolute inset-[10px] rounded-full overflow-hidden bg-white">
                <img
                  v-if="app?.icon"
                  :src="app.icon"
                  class="w-full h-full rounded-full object-cover"
                >
                <div
                  v-else
                  class="w-full h-full rounded-full bg-gray-200"
                />
              </div>
            </div>
            <div class="flex justify-between items-baseline w-full">
              <div class="text-[18px] font-bold">
                {{ app?.name }}
              </div>
              <div
                class="text-[14px] text-gray-500 text-right"
              >
                Estimated time {{ planData.estimated_build_time }}
              </div>
            </div>
          </div>
          <!-- Features selection (shown before build starts) -->
          <!-- Pick features message -->
          <div class="flex items-start gap-[8px] mb-[12px]">
            <div class="flex items-center justify-center w-[24px] h-[20px]">
              <span class="typing-dots text-[#668AF1]">...</span>
            </div>
            <span class="text-[14px] leading-[20px]">Pick the features you'd like to include:</span>
          </div>
          <!-- Features checkbox list -->
          <div class="p-[12px] rounded-[8px] border border-gray-100">
            <div class="space-y-[8px]">
              <label
                v-for="(feature, idx) in planFeatures"
                :key="idx"
                class="flex items-center gap-[8px] cursor-pointer"
              >
                <input
                  v-model="feature.selected"
                  :disabled="buildStarted"
                  type="checkbox"
                  class="checkbox checkbox-sm checkbox-neutral"
                >
                <span
                  class="text-[14px]"
                  :class="{ 'font-medium': feature.selected, 'text-gray-400': !feature.selected }"
                >
                  {{ feature.label }}
                </span>
              </label>
              <!-- Custom feature inputs -->
              <label
                v-for="(customFeature, idx) in customFeatures"
                :key="'custom-' + idx"
                class="flex items-center gap-[8px] cursor-pointer"
              >
                <input
                  v-model="customFeature.selected"
                  :disabled="buildStarted"
                  type="checkbox"
                  class="checkbox checkbox-sm checkbox-neutral"
                >
                <input
                  v-model="customFeature.label"
                  type="text"
                  class="custom-feature-input flex-1 text-[14px] p-[4px] border-b border-gray-200 focus:border-gray-400 outline-none"
                  :class="{ 'font-medium': customFeature.selected, 'text-gray-400': !customFeature.selected }"
                  placeholder="Type a specific feature..."
                >
              </label>
              <!-- Add custom feature button -->
              <div
                v-if="!buildStarted"
                class="flex items-center gap-[8px] cursor-pointer text-gray-500 hover:text-gray-700"
                @click="addCustomFeature"
              >
                <PlusIcon class="size-[16px]" />
                <span class="text-[14px]">Add a custom feature</span>
              </div>
            </div>
          </div>
          <!-- Auto select timer -->
          <div
            v-if="autoSelectCountdown > 0"
            class="text-center text-[14px] text-gray-400 mt-[12px]"
          >
            Auto select all in {{ formatCountdown(autoSelectCountdown) }}
          </div>
          <!-- Action buttons -->
          <div class="flex gap-[12px] mt-[16px]">
            <button
              class="flex-1 py-[12px] px-[16px] rounded-[40px] border border-[#668AF1] text-[#668AF1] font-medium hover:bg-blue-50 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="suggestMoreLoading || buildStarted"
              @click="suggestMore"
            >
              <span
                v-if="suggestMoreLoading"
                class="loading loading-spinner loading-sm"
              />
              <span v-else>Suggest More</span>
            </button>
            <button
              class="flex-1 py-[12px] px-[16px] rounded-[40px] bg-[#1F2937] text-white font-medium hover:bg-gray-800 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="suggestMoreLoading || buildStarted"
              @click="() => createApp()"
            >
              <span
                v-if="buildStarted"
                class="loading loading-spinner loading-sm"
              />
              <span v-else>Create</span>
            </button>
          </div>
        </div>
        <!-- Making changes state (when no progress events received) -->
        <div
          v-else-if="showMakingChanges"
          class="flex items-start gap-[8px] w-full"
        >
          <div class="flex items-center justify-center w-[24px] h-[20px]">
            <span class="typing-dots text-[#668AF1]">...</span>
          </div>
          <span class="text-[14px] leading-[20px]">Making changes now</span>
        </div>
      </div>
      <div
        class="flex flex-col items-center gap-[8px]"
        :class="{'input-float page-align': tabActive == 'preview'}"
      >
        <div class="flex md:hidden justify-center gap-[4px] p-[4px] rounded-[40px] bg-[#F2F2F2]">
          <div
            class="py-[6px] px-[29px] cursor-pointer"
            :class="{'tab-active': tabActive == 'chat'}"
            @click="tabActive = 'chat'"
          >
            Chat
          </div>
          <div
            class="py-[6px] px-[29px] cursor-pointer"
            :class="{'tab-active': tabActive == 'preview'}"
            @click="tabActive = 'preview'"
          >
            Preview
          </div>
        </div>
        <div
          v-show="tabActive !== 'preview'"
          class="w-full bottom-0 rounded-[16px] bg-[#F2F2F2]"
        >
          <textarea
            ref="textareaRef"
            v-model="inputText"
            :disabled="completionLoading"
            class="w-full h-[55px] max-h-[250px] text-[14px] p-[12px] pb-0 rounded-[16px] border-none resize-none"
            maxlength="1000"
            placeholder="Ask Ability anything..."
            @keydown.enter="handleEnter"
            @input="updateTextareaHeight"
          />
          <div class="flex justify-end pr-[8px] pb-[8px]">
            <button
              class="w-[32px] h-[32px] p-0 rounded-full shadow-none btn btn-neutral"
              :disabled="!completionLoading && !inputText.length"
              @click="completionToggle"
            >
              <div
                v-if="completionLoading"
                class="size-[18px] rounded-[3px] bg-white"
              />
              <ArrowUpRightIcon
                v-else
                class="size-[18px]"
              />
            </button>
          </div>
        </div>
      </div>
    </div>
    <div
      class="hidden md:block flex-1"
      :class="{'preview-full': tabActive == 'preview'}"
    >
      <div class="flex w-full h-full bg-[#F7F3ED]">
        <div
          v-if="buildStatus === 'error'"
          class="w-full h-full"
        >
          <div class="flex flex-col items-center justify-center gap-[34px] h-full text-[18px]">
            <img
              src="@/assets/build-error.png"
              class="size-[55px]"
            >
            <div class="max-w-[400px] text-[18px] text-center">
              We’re really sorry — your app stopped coding midway. Just submit your prompt again and we’ll build it again immediately.
            </div>
          </div>
        </div>
        <AppPreview
          v-else-if="shouldShowPreview"
          :key="previewKey"
          :app-id="appId"
        />
      </div>
    </div>
  </main>
  <EditAppItem
    v-if="app && showEdit"
    :data="app"
    @updated="itemUpdated"
    @close="closeEditItemModal"
  />
</template>

<script setup lang="ts">
import { ref, reactive, watch, watchEffect, onUnmounted, nextTick, onMounted, computed } from 'vue';
import { marked } from 'marked';
import { useRoute } from 'vue-router';
import { useQuery } from '@tanstack/vue-query';
import {
  ArrowLeftIcon, ArrowUpRightIcon, PencilSquareIcon, CheckIcon, PlusIcon, XCircleIcon,
} from '@heroicons/vue/24/outline';
import AppPreview from '@/components/AppPreview.vue';
import Skeleton from '@/components/Skeleton.vue';
import EditAppItem from '@/components/EditAppItem.vue';
import router from '@/router';
import { Message } from '@/types';
import { AppDetail, AppCategories, AppCategory, ChatEvent, AppStage } from '@/types/app';
import { useModalStore } from '@/stores/modal';
import { useGetAppDetail, useInitAppInfo, useAppStage } from '@/composables/app';
import { getAppEvents } from '@/services/app';
import { formatDate, uid, routerBack } from '@/utils';
import { toast } from '@/utils/toast';
import defaultIcon from '@/assets/app-icon.png';

const SUGGEST_PROMPT = 'suggest more features';

const SELECTED_FEATURES_PREFIX = 'selected features:';

// Plan mode types
interface PlanFeature {
  label: string;
  description: string;
  selected: boolean;
}

interface CustomFeature {
  label: string;
  selected: boolean;
}

interface PlanData {
  project: string;
  estimated_build_time: string;
  features: PlanFeature[];
}

interface ProgressItem {
  content: string;
  status: 'completed' | 'in_progress' | 'pending';
  activeForm: string;
}

const route = useRoute();
const appId = route.params.id as string;
let initQuestion = route.query.initQuestion as string;

const showEdit = ref(false);
const completionLoading = ref(false);
const messages = ref<Message[]>([]);
const inputText = ref('');
const tabActive = ref('chat');
const app = ref<AppDetail>();
const shouldShowPreview = ref(false);
const abortController = ref<AbortController | null>(null);
// Plan mode state
const planData = ref<PlanData | null>(null);
let planFeatures = reactive<PlanFeature[]>([]);
let customFeatures = reactive<CustomFeature[]>([]);
const planLoading = ref(false);
const buildStarted = ref(false);
const suggestMoreLoading = ref(false);
const autoSelectCountdown = ref(0);
let autoSelectTimer: ReturnType<typeof setInterval> | null = null;
const currentPrompt = ref('');
const planError = ref(false);
const previewKey = ref<string>(uid());
const { data: appData, isFetching: loading } = useGetAppDetail(appId);
const { data: appStage } = useAppStage(appId, {
  refetchInterval: 10000,
  retry: false,
  cacheTime: 0,
});
const shouldPollingEvents = computed(() => {
  const result = !completionLoading.value && !suggestMoreLoading.value && !planError.value && (appStage?.value === AppStage.Planning || appStage?.value === AppStage.Building);
  return result;
});
const { data: eventsData, isLoading: loadingEventsData } = useQuery({
  queryKey: [`apps:${appId}:events`],
  queryFn: async () => getAppEvents(appId),
  refetchInterval: () => shouldPollingEvents.value ? 10000 : false,
  retry: false,
  enabled: !initQuestion,
});
const messagesContainer = ref<HTMLDivElement | null>(null);
const textareaRef = ref<HTMLTextAreaElement | null>(null);
const buildStatus = ref<'preparing' | 'error' | null>(null);
const { mutate: initAppInfo, isPending: initAppInfoPending } = useInitAppInfo();

const showMakingChanges = computed(() => {
  if (messages.value[messages.value.length - 1]?.type === 'error') return false;

  let userMessageIndex = 0;
  let progressMessageIndex = 0;
  messages.value.forEach((msg, i) => {
    if (msg.role === 'user' && msg.type === 'message') {
      userMessageIndex = i;
    }
    if (msg.type === 'progress') {
      progressMessageIndex = i;
    }
  });
  const hasProgress = progressMessageIndex > userMessageIndex;

  // Case 1: Real-time streaming (createApp is running)
  if (buildStarted.value && completionLoading.value) {
    if (buildStatus.value === 'preparing' || buildStatus.value === 'error') return false;
    if (planData.value) return false;
    return !hasProgress;
  }

  // Case 2: Page refreshed, has data, still polling for updates
  if (messages.value.length > 2 && shouldPollingEvents.value && !hasProgress) {
    return true;
  }

  return false;
});

const getProgressPercentage = (todos: ProgressItem[]) => {
  if (!todos?.length) return 0;
  const completed = todos.filter(item => item.status === 'completed').length;
  return (completed / todos.length) * 100;
};

let autoScrollEnabled = true;
let lastScrollTop = 0;

const updateTextareaHeight = async () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.overflowY = 'hidden';
    const newHeight = Math.max(textareaRef.value.scrollHeight, 55);
    textareaRef.value.style.height = newHeight + 'px';
    textareaRef.value.style.overflowY = 'auto';
  }
}

const handleEnter = (e) => {
  if (e.ctrlKey || e.metaKey || e.shiftKey) return;
  e.preventDefault();
  if (messages.value.length > 2) {
    createApp(inputText.value);
  } else {
    completion();
  }
}

// Format countdown timer
const formatCountdown = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// Start auto-select countdown
const startAutoSelectCountdown = (seconds = 300) => {
  autoSelectCountdown.value = seconds;
  if (autoSelectTimer) {
    clearInterval(autoSelectTimer);
  }
  autoSelectTimer = setInterval(() => {
    autoSelectCountdown.value--;
    if (autoSelectCountdown.value <= 0) {
      if (autoSelectTimer) {
        clearInterval(autoSelectTimer);
        autoSelectTimer = null;
      }
      // Auto select all features
      planFeatures.forEach(f => {
        f.selected = true;
      });
    }
  }, 1000);
};

// Stop auto-select countdown
const stopAutoSelectCountdown = () => {
  if (autoSelectTimer) {
    clearInterval(autoSelectTimer);
    autoSelectTimer = null;
  }
  autoSelectCountdown.value = 0;
};

// Add custom feature
const addCustomFeature = () => {
  startAutoSelectCountdown();
  customFeatures.push({
    label: '',
    selected: true
  });
  // Auto focus the new input
  nextTick(() => {
    const inputs = document.querySelectorAll('.custom-feature-input');
    const lastInput = inputs[inputs.length - 1] as HTMLInputElement;
    if (lastInput) {
      lastInput.focus();
    }
  });
};

// Suggest more features - call API with mode: "plan"
const suggestMore = async () => {
  suggestMoreLoading.value = true;
  planLoading.value = true;

  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/chat/completion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ app_id: appId, prompt: SUGGEST_PROMPT, mode: 'plan' }),
    });

    if (response.status === 401) {
      const modalStore = useModalStore();
      modalStore.showLogin = true;
      return;
    }
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split(/\r?\n/).filter(x => x.trim() !== '');

      for (const line of lines) {
        const jsonData = JSON.parse(line);
        if (jsonData.event === 'plan') {
          planData.value = jsonData.data;
          planFeatures = reactive(jsonData.data.features);
          planLoading.value = false;
          startAutoSelectCountdown();
        }
      }
    }
  } catch (error) {
    console.error('Suggest more error:', error);
    toast.error('Failed to get more suggestions');
    planLoading.value = false;
  } finally {
    suggestMoreLoading.value = false;
  }
};

// Create app - call API without mode: "plan"
const createApp = async (prompt?: string) => {
  let actualPrompt = prompt;

  if (prompt) {
    messages.value.push({
      id: uid(),
      timestamp: new Date().toISOString(),
      role: 'user',
      type: 'message',
      data: prompt,
    } as Message);
    inputText.value = '';
    scrollToBottom();
  } else {
    const selectedFeatures = [
      ...planFeatures.filter(f => f.selected),
      ...customFeatures.filter(f => f.selected && f.label.trim()),
    ];
    if (selectedFeatures.length === 0) return;
    stopAutoSelectCountdown();
    const featuresText = selectedFeatures.map(f => f.label).join(', ');
    actualPrompt = `${SELECTED_FEATURES_PREFIX} ${featuresText}`;
  }

  buildStarted.value = true;
  completionLoading.value = true;
  buildStatus.value = 'preparing';

  try {
    const token = localStorage.getItem('token');
    abortController.value = new AbortController();

    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/chat/completion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ app_id: appId, prompt: actualPrompt }),
      signal: abortController.value.signal,
    });

    if (response.status === 401) {
      const modalStore = useModalStore();
      modalStore.showLogin = true;
      return;
    }

    if (response.status === 402) {
      buildStatus.value = null;
      buildStarted.value = false;
      completionLoading.value = false;
      messages.value.push({
        id: uid(),
        timestamp: new Date().toISOString(),
        role: 'assistant',
        type: 'error',
        data: 'Usage limit exceeded for this app, please try to create a new app instead.',
      } as Message);
      scrollToBottom();
      return;
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    const decoder = new TextDecoder();
    autoScrollEnabled = true;
    buildStatus.value = null;
    planData.value = null;
    planFeatures = reactive([]);
    shouldShowPreview.value = true;
    let shouldUpdatePreviewKey = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split(/\r?\n/).filter(x => x.trim() !== '');

      for (const line of lines) {
        const jsonData: ChatEvent = JSON.parse(line);
        if (jsonData.event === 'progress') {
          const msg = eventToMessage(jsonData);
          if (!msg) continue;
          let userMessageIndex = -1;
          let progressMessageIndex = -1;
          let i = messages.value.length - 1;
          while (userMessageIndex < 0) {
            const m = messages.value[i];
            if (m?.type === 'progress') {
              progressMessageIndex = i;
            } else if (m?.type === 'message' && m?.role === 'user') {
              userMessageIndex = i;
              break;
            }
            i -= 1;
          }
          if (progressMessageIndex > userMessageIndex) {
            messages.value[progressMessageIndex] = msg;
          } else {
            messages.value.push(msg);
          }
          if (jsonData.data.every((x: ProgressItem) => x.status === 'completed')) {
            shouldUpdatePreviewKey = true;
          }
          scrollToBottom();
        } else if (jsonData.event === 'message') {
          messages.value.push(eventToMessage(jsonData) as Message);
          scrollToBottom();
        } else if (jsonData.event === 'tool_use') {
          if (jsonData.data.name === 'Edit' || jsonData.data.name === 'Write') {
            shouldUpdatePreviewKey = true;
          }
        } else if (jsonData.event === 'end') {
          console.log(jsonData.data);
          if (shouldUpdatePreviewKey) {
            previewKey.value = uid();
            toast.success('App successfully created');
            if (Notification?.permission === 'granted') {
              new Notification('App completed', { body: 'Your app is completed! Check it out.' });
            }
          }
        } else if (jsonData.event === 'error') {
          toast.error(jsonData.data);
          buildStatus.value = 'error';
          planError.value = true;
        }
      }
    }
  } catch (error: any) {
    if (error.name !== 'AbortError') {
      toast.error('Error state');
      buildStatus.value = 'error';
      planError.value = true;
      if (Notification?.permission === 'granted') {
        new Notification('Build stopped', { body: 'Sorry, your app stopped coding. Please re-enter your prompt to start a new build' });
      }
    }
    console.error('Fetch error:', error);
  }
  completionLoading.value = false;
};

const completion = async () => {
  if (!appId || !inputText.value.trim()) return;
  completionLoading.value = true;
  const prompt = inputText.value;
  currentPrompt.value = prompt;
  tabActive.value = 'chat';

  // Reset plan mode state
  planData.value = null;
  planFeatures = reactive([]);
  buildStarted.value = false;
  customFeatures = reactive([]);
  planError.value = false;
  stopAutoSelectCountdown();

  messages.value.push({
    id: uid(),
    timestamp: new Date().toISOString(),
    role: 'user',
    type: 'message',
    data: prompt,
  } as Message);
  inputText.value = '';

  try {
    const token = localStorage.getItem('token');
    abortController.value = new AbortController();
    buildStatus.value = 'preparing';
    scrollToBottom();

    if (!initAppInfoPending.value && !app.value?.name) {
      initAppInfo(
        { id: appId, prompt },
        {
          onSuccess: (data) => {
            if (app.value && data) {
              app.value.name = data.name;
              if (data.description) {
                app.value.description = data.description;
              }
              if (data.category) {
                app.value.category = data.category as AppCategory;
              }
              if (data.icon) {
                app.value.icon = data.icon;
              }
            }
          },
        }
      );
    }

    // Call API with mode: "plan" first
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/chat/completion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ app_id: appId, prompt, mode: 'plan' }),
      signal: abortController.value.signal,
    });
    if (response.status === 401) {
      const modalStore = useModalStore();
      modalStore.showLogin = true;
      return;
    }
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }
    const decoder = new TextDecoder();
    autoScrollEnabled = true;
    planLoading.value = true;

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break
      }
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split(/\r?\n/).filter(x => x.trim() !== '');
      for (const line of lines) {
        const jsonData = JSON.parse(line);

        if (jsonData.event === 'plan') {
          // Handle plan event
          planData.value = jsonData.data;
          planFeatures = reactive(jsonData.data.features);
          planLoading.value = false;
          buildStatus.value = null;
          startAutoSelectCountdown();
          scrollToBottom();
        } else if (jsonData.event === 'message') {
          // Handle message event (when no plan is returned)
          planLoading.value = false;
          buildStatus.value = null;
          messages.value.push(eventToMessage(jsonData) as Message);
          scrollToBottom();
        } else if (jsonData.event === 'error') {
          toast.error(jsonData.data);
          buildStatus.value = 'error';
          planLoading.value = false;
        }
      }
    }
    // Reset status if no plan event was received (e.g. tool_use, message only)
    if (buildStatus.value === 'preparing') {
      buildStatus.value = null;
    }
    planLoading.value = false;
  } catch (error: any) {
    if (error.name !== 'AbortError') {
      toast.error('Error state');
      buildStatus.value = 'error';
      planLoading.value = false;
      if (Notification?.permission === 'granted') {
        new Notification('Build stopped', { body: 'Sorry, your app stopped coding. Please re-enter your prompt to start a new build' });
      }
    }
    console.error('Fetch error:', error)
  }
  completionLoading.value = false;
}

const showEditItemModal = () => {
  showEdit.value = true;
}

const closeEditItemModal = () => {
  showEdit.value = false;
}

const itemUpdated = (newData) => {
  closeEditItemModal();
  app.value = {
    ...app.value,
    ...newData,
  };
}

const stopCompletion = () => {
  if (abortController.value) {
    abortController.value.abort();
    abortController.value = null;
    completionLoading.value = false;
    buildStatus.value = null;
  }
}

const completionToggle = () => {
  if (!completionLoading.value) {
    if (messages.value.length > 2) {
      createApp(inputText.value);
    } else {
      completion();
    }
  } else {
    stopCompletion();
  }
}

const eventToMessage = (event: ChatEvent): Message | null => {
  if (event.event !== 'message' && event.event !== 'plan' && event.event !== 'progress') return null;

  if (event.event === 'message' && (event.data === SUGGEST_PROMPT || event.data.startsWith(SELECTED_FEATURES_PREFIX))) {
    return null;
  }

  const msg: Message = {
    id: event.id,
    timestamp: event.timestamp,
    role: event.role,
    type: event.event,
    data: event.data,
  };

  if (msg.type === 'message') {
    msg.htmlContent = marked(msg.data, { async: false });
  }

  return msg;
};

const scrollToBottom = () => {
  const container = messagesContainer.value;
  if (!container || !autoScrollEnabled) return;
  nextTick(() => {
    container.scrollTop = container.scrollHeight;
  });
};

const handleScroll = () => {
  const container = messagesContainer.value
  if (!container) return;

  // If the scrolls to the bottom, re enable automatic scrolling
  // If scrolling upwards, turn off automatic scrolling
  const threshold = 50;
  const isAtBottom = container.scrollHeight - container.scrollTop - container.clientHeight <= threshold;
  const isUserScroll = container.scrollTop < lastScrollTop
  lastScrollTop = container.scrollTop
  if (isAtBottom) {
    autoScrollEnabled = true;
  } else if (isUserScroll && !isAtBottom) {
    autoScrollEnabled = false;
  }
};

watch(appData, (newData) => {
  if (newData) {
    app.value = { ...newData };
    if (initQuestion) {
      inputText.value = initQuestion;
      completion();
      initQuestion = '';
      setTimeout(() => {
        router.replace({path: window.location.pathname});
      }, 1000);
    }
  }
});

watchEffect(async () => {
  if (eventsData.value) {
    let plan: PlanData | null = null;
    const msgs: Message[] = [];
    eventsData.value.forEach(event => {
      if (event.event === 'error') {
        planError.value = true;
      } else if (event.event === 'plan') {
        plan = event.data;
      } else if (event.event === 'progress') {
        plan = null;
      }

      const msg = eventToMessage(event);
      if (msg) {
        msgs.push(msg);
      }
    });

    if (plan && shouldPollingEvents) {
      planData.value = plan;
      // @ts-expect-error - plan.features type mismatch
      planFeatures = reactive(plan.features);
      startAutoSelectCountdown();
    }

    if (msgs.length) {
      messages.value = msgs;
      scrollToBottom();
    }

    shouldShowPreview.value = true;
  }
});

watchEffect(() => {
  if (appStage.value === AppStage.Built) {
    previewKey.value = uid();
  }
});

onMounted(() => {
  // Obtain notification permission
  if (Notification?.permission === 'default') {
    Notification.requestPermission();
  }
});

onUnmounted(() => {
  stopAutoSelectCountdown();
});
</script>

<style scoped>
.ball {
  background-size: 100% 100%;
  background-repeat: no-repeat;
  background-image: url(@/assets/gradient-ball.png);
}
.tab-active {
  border-radius: 40px;
  background-color: white;
}
.input-float {
  position: fixed;
  left: 0;
  bottom: 50px;
  z-index: 1;
  width: 100%;
}
.preview-full {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: block;
}
.typing-dots {
  font-weight: bold;
  letter-spacing: 2px;
  animation: blink 1.4s infinite;
}
@keyframes blink {
  0%, 20% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    opacity: 1;
  }
}
.plan-card-shadow {
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.08);
}

:deep(pre) {
  max-width: 100%;
  background-color: #f5f5f5;
  border-radius: 6px;
  padding: 12px;
  margin: 8px 0;
}

:deep(pre code) {
  white-space: pre-wrap;
  word-break: break-word;
}

:deep(:not(pre) > code) {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  word-break: break-word;
}
</style>
