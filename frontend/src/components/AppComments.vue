<script setup lang="ts">
import { reactive, ref, watch } from 'vue';
import { XMarkIcon, EyeIcon, HandThumbUpIcon, EllipsisVerticalIcon, ChevronDownIcon, CheckCircleIcon } from '@heroicons/vue/24/outline';
import { ArrowDownCircleIcon, HandThumbUpIcon as HandThumbUpIconActive } from '@heroicons/vue/24/solid';

import Modal from '@/components/Modal.vue';
import DefaultAvatar from '@/components/DefaultAvatar.vue';
import LoadingButton from '@/components/LoadingButton.vue';

import { formatDate, formatNumber } from '@/utils';
import { useUserStore } from '@/stores/user';
import { useAppLikeToggle, useCheckAppLike, useCommentLikeToggle, useCreateComment, useDeleteComment, useGetAppComments, useGetSubComments } from '@/composables/app';
import { AppComment, AppSubComment, AppCommunityDetail, AppCategories } from '@/types/app';
import { getSubComments } from '@/services/app';
import { useCheckFollow, useFollowToggle } from '@/composables/user';

const emit = defineEmits<{
  'close': [];
  'likeChange': [number];
  'clickBookmark': [];
  'followerChange': [number];
}>();

const props = defineProps<{
  app: AppCommunityDetail,
  show: boolean,
}>();

const userStore = useUserStore();
const modalShow = ref(props.show);
const isVisible = ref(false);
const commentValue = ref('');
const replyCommentId = ref<string | null>(null);
const replyCommentValue = ref('');
const openReplies = ref({});
const total = ref(0);
const comments = ref<AppComment[]>([]);
const removeConfig = reactive<{
  id: string | null,
  parentId: string | null,
}>({
  id: null,
  parentId: null,
});
const options = reactive({
  page: 1,
  limit: 20,
});
const subCommentQueries = ref({});
const subComments = ref<{
  [key: string]: AppSubComment[]
}>({});
const {data: listData} = useGetAppComments(props.app.id, options);
const { mutateAsync: createComment, isPending: createLoading } = useCreateComment();
const { mutateAsync: deleteComment, isPending: deleteLoading } = useDeleteComment();
const { mutateAsync: followToggle, isPending: followToggleLoading } = useFollowToggle();
const { mutateAsync: appLikeToggle, isPending: appLikeToggleLoading } = useAppLikeToggle();
const commentLikeToggleRunning = {};
const { mutateAsync: commentLikeToggle } = useCommentLikeToggle();
const isFollowing = ref(false);
const isLike = ref(false);
const { data: followData } = useCheckFollow(props.app.creator.id);
const { data: likeData } = useCheckAppLike(props.app.id);

watch(followData, (newData) => {
  if (newData) {
    isFollowing.value = newData;
  }
}, { immediate: true });

watch(likeData, (newData) => {
  if (newData) {
    isLike.value = newData;
  }
}, { immediate: true });


watch(listData, (newData) => {
  if (newData) {
    total.value = newData.total;
    // Clone each comment and its creator to avoid mutating readonly response objects in local state.
    const newComments = newData.data.map(c => ({ ...c, creator: { ...c.creator } }));
    comments.value = [...comments.value, ...newComments];
  }
}, {immediate: true});

watch(() => comments, (newData) => {
  if (newData) {
    newData.value.forEach(comment => {
      if (!subCommentQueries.value[comment.id]) {
        subCommentQueries.value[comment.id] = useGetSubComments(
          comment.id,
          { enabled: false }
        );
      }
    });
  }
}, { immediate: true });

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

const cancelComment = () => {
  commentValue.value = '';
}

const changereplyCommentId = (id: string) => {
  replyCommentId.value = id;
}

const cancelReplyComment = () => {
  replyCommentId.value = null;
  replyCommentValue.value = '';
}

const switchOpenReplies = async (id: string) => {
  if (typeof openReplies.value[id] === 'undefined') {
    openReplies.value[id] = false;
    const data = await getSubComments(id);
    // Clone each comment and its creator to avoid mutating readonly response objects in local state.
    subComments.value[id] = data.map(c => ({ ...c, creator: { ...c.creator } }));
  }
  openReplies.value[id] = !openReplies.value[id];
}

const showDeleteCommentModal = (id: string, parentId: string | null) => {
  removeConfig.id = id;
  removeConfig.parentId = parentId;
}

const closeDeleteCommentModal = () => {
  removeConfig.id = null;
}

const clickFollowToggle = async () => {
  if (followToggleLoading.value) return;
  await followToggle(props.app.creator.id);
  isFollowing.value = !isFollowing.value;
  emit('followerChange', isFollowing.value ? 1 : -1);
}

const clickAppLikeToggle = async () => {
  if (appLikeToggleLoading.value) return;
  await appLikeToggle(props.app.id);
  isLike.value = !isLike.value;
  emit('likeChange', isLike.value ? 1 : -1);
}

const clickCommentLikeToggle = async (comment) => {
  if (commentLikeToggleRunning[comment.id]) return;
  try {
    commentLikeToggleRunning[comment.id] = true;
    await commentLikeToggle(comment.id);
    comment.is_like = !comment.is_like;
    comment.likes_count += comment.is_like ? 1 : -1;
  } finally {
    commentLikeToggleRunning[comment.id] = false;
  }
}

const submit = async (parentId: string | null) => {
  if (createLoading.value) return false;
  const value = parentId ? replyCommentValue.value : commentValue.value;
  const commentId = await createComment({
    app_id: props.app.id,
    content: value,
    parent_id: parentId
  });
  const time = new Date().toISOString();
  const commentData = {
    id: commentId,
    content: value,
    replies_count: 0,
    likes_count: 0,
    created_at: time,
    creator: {
      id: userStore.profile!.id,
      full_name: userStore.profile!.full_name,
      avatar_url: userStore.profile!.avatar_url,
    }
  };
  if (!parentId) {
    comments.value.unshift(commentData);
    total.value++;
    commentValue.value = '';
  } else {
    if (typeof subComments.value[parentId] === 'undefined') {
      subComments.value[parentId] = [];
    }
    const data = {...commentData, parent_id: parentId};
    subComments.value[parentId].unshift(data);
    replyCommentValue.value = '';

    const parentCommentIndex = comments.value.findIndex(c => c.id === parentId);
    comments.value[parentCommentIndex]!.replies_count++;
    cancelReplyComment();
  }
}

const destory = async () => {
  if (deleteLoading.value || !removeConfig.id) return false;
  await deleteComment(removeConfig.id);
  if (!removeConfig.parentId) {
    const index = comments.value.findIndex(c => c.id === removeConfig.id);
    comments.value.splice(index, 1);
  } else {
    const index = subComments.value[removeConfig.parentId]!.findIndex(c => c.id === removeConfig.id);
    subComments.value[removeConfig.parentId]!.splice(index, 1);

    const parentCommentIndex = comments.value.findIndex(c => c.id === removeConfig.parentId);
    comments.value[parentCommentIndex]!.replies_count--;
  }
  removeConfig.id = null;
  removeConfig.parentId = null;
}

changeVisible();
</script>

<template>
  <dialog
    class="modal modal-bottom"
    :open="isVisible"
  >
    <div class="relative w-full max-h-[80%] py-[24px] lg:py-[48px] px-[16px] lg:px-[140px] rounded-t-[32px] modal-box">
      <XMarkIcon
        class="absolute top-[16px] right-[16px] size-[24px] text-[#999999] cursor-pointer"
        @click="closeModal"
      />
      <div class="flex flex-col gap-[32px]">
        <div class="flex lg:items-center flex-col lg:flex-row gap-[12px]">
          <div class="flex">
            <RouterLink :to="`/users/${app.creator.id}/community`">
              <img
                v-if="app.creator.avatar_url"
                :src="app.creator.avatar_url"
                class="size-[40px] mr-[8px] rounded-full"
              >
              <DefaultAvatar
                v-else
                class="size-[40px]"
              />
            </RouterLink>
            <div class="flex flex-col gap-[4px] mr-[12px]">
              <RouterLink
                :to="`/users/${app.creator.id}/community`"
                class="font-bold"
              >
                {{ app.creator.full_name || 'Anonymous' }}
              </RouterLink>
              <div class="text-[#999999] text-[14px]">
                {{ formatNumber(app.creator.followers_count) }} followers
              </div>
            </div>
          </div>
          <div
            class="flex-1 flex justify-between lg:flex-row"
            :class="[
              (followData !== undefined && userStore.profile) && app.creator.id !== userStore.profile.id ? 'flex-row-reverse' : ''
            ]"
          >
            <div
              v-if="(followData !== undefined && userStore.profile) && app.creator.id !== userStore.profile.id"
              class="flex items-center gap-[8px] py-[8px] px-[12px] ml-auto md:ml-0 cursor-pointer rounded-[40px] bg-[#333333]"
              :class="[isFollowing ? 'bg-[#CCCCCC]' : 'bg-[#333333]']"
              @click="clickFollowToggle"
            >
              <CheckCircleIcon
                v-if="isFollowing"
                class="size-[24px] text-white"
              />
              <div class="text-white">
                {{ isFollowing ? 'Following' : 'Follow' }}
              </div>
            </div>
            <div class="flex gap-[8px] md:ml-auto">
              <div
                class="flex items-center gap-[8px] py-[8px] px-[16px] cursor-pointer rounded-[40px] bg-[#F2F2F2]"
                @click="emit('clickBookmark')"
              >
                <ArrowDownCircleIcon class="text-black size-[24px]" />
                <div class="text-[#666666]">
                  {{ app.bookmarks_count }}
                </div>
              </div>
              <div
                v-if="likeData !== undefined"
                class="flex items-center gap-[8px] cursor-pointer py-[8px] px-[16px] rounded-[40px] bg-[#F2F2F2]"
                @click="clickAppLikeToggle"
              >
                <!-- <img src="@/assets/thumb-icon.svg" class="size-[16px]"> -->
                <HandThumbUpIconActive
                  v-if="isLike"
                  class="size-[16px]"
                />
                <HandThumbUpIcon
                  v-else
                  class="size-[16px]"
                />
                <div class="text-[#666666]">
                  {{ formatNumber(app.likes_count) }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="flex flex-col">
          <div class="font-bold mb-[8px]">
            {{ app.name }}
          </div>
          <div class="mb-[16px]">
            {{ app.description }}
          </div>
          <div class="flex items-center gap-[6px] leading-none">
            <div
              v-if="app.category"
              class="text-[12px] py-[4.5px] px-[8px] rounded-[20px] bg-[#F2F2F2]"
            >
              {{ AppCategories[app.category] }}
            </div>
            <div class="flex items-center gap-[4px]">
              <EyeIcon class="size-[12px]" />
              <div class="text-[#999999] text-[12px]">
                {{ formatNumber(app.page_view) }}
              </div>
            </div>
            <div class="text-[#999999] text-[12px]">
              | Updated {{ formatDate(app.updated_at) }}
            </div>
          </div>
        </div>
        <div class="flex flex-col gap-[24px]">
          <div class="text-[20px] font-bold">
            {{ total }} Comments
          </div>
          <div class="flex pb-[8px] border-b-1 border-[#E5E5E5]">
            <img
              v-if="userStore.profile?.avatar_url"
              :src="userStore.profile?.avatar_url"
              class="size-[40px] mr-[8px] rounded-full"
            >
            <DefaultAvatar
              v-else
              class="size-[40px]"
            />
            <div class="flex-1 flex flex-col">
              <div class="font-bold mb-[4px]">
                You
              </div>
              <div class="flex gap-[16px] h-[40px]">
                <input
                  v-model="commentValue"
                  type="text"
                  class="w-full text-[14px] leading-[38px]"
                  placeholder="Add a comment.."
                >
                <template
                  v-if="commentValue"
                >
                  <div
                    class="h-[40px] leading-[38px] px-[16px] md:px-[24px] cursor-pointer"
                    @click="cancelComment"
                  >
                    Cancel
                  </div>
                  <div
                    class="h-[40px] text-[#668AF1] leading-[38px] px-[16px] md:px-[24px] cursor-pointer border-1 border-[#668AF1] rounded-[40px]"
                    @click="submit(null)"
                  >
                    Comment
                  </div>
                </template>
              </div>
            </div>
          </div>
          <div class="flex flex-col gap-[24px]">
            <div
              v-for="comment in comments"
              :key="comment.id"
              class="flex flex-col gap-[8px]"
            >
              <div class="flex">
                <RouterLink :to="`/users/${comment.creator.id}/community`">
                  <img
                    v-if="comment.creator.avatar_url"
                    :src="comment.creator.avatar_url"
                    class="size-[40px] mr-[8px] rounded-full"
                  >
                  <DefaultAvatar
                    v-else
                    class="size-[40px]"
                  />
                </RouterLink>
                <div class="flex-1 flex flex-col">
                  <div class="flex items-baseline gap-[4px] leading-none mb-[4px]">
                    <RouterLink
                      :to="`/users/${comment.creator.id}/community`"
                      class="font-bold"
                    >
                      {{ comment.creator.full_name || 'Anonymous' }}
                    </RouterLink>
                    <div class="text-[#999999] text-[12px]">
                      {{ formatDate(comment.created_at) }}
                    </div>
                  </div>
                  <div class="text-[14px] mb-[8px]">
                    {{ comment.content }}
                  </div>
                  <div class="flex items-center gap-[6px] text-[#999999] text-[12px] leading-none">
                    <div
                      class="flex items-center gap-[5px] cursor-pointer"
                      @click="clickCommentLikeToggle(comment)"
                    >
                      <HandThumbUpIconActive
                        v-if="comment.is_like"
                        class="size-[12px]"
                      />
                      <HandThumbUpIcon
                        v-else
                        class="size-[12px]"
                      />
                      <div>{{ comment.likes_count }}</div>
                    </div>
                    <div>|</div>
                    <div
                      class="cursor-pointer"
                      @click="changereplyCommentId(comment.id)"
                    >
                      Reply
                    </div>
                  </div>
                </div>
                <div
                  v-if="comment.creator.id === userStore.profile?.id"
                  class="ml-auto dropdown dropdown-end"
                >
                  <div
                    tabindex="0"
                    role="button"
                    class="cursor-pointer"
                  >
                    <EllipsisVerticalIcon class="size-[24px] ml-auto" />
                  </div>
                  <ul
                    tabindex="0"
                    class="w-[174px] p-[4px] rounded-[8px] bg-white shadow-sm dropdown-content menu"
                  >
                    <li>
                      <div
                        class="p-[8px]"
                        @click="showDeleteCommentModal(comment.id, null)"
                      >
                        Delete
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
              <div
                v-if="replyCommentId === comment.id"
                class="flex gap-[16px] h-[49px] ml-[40px] pb-[8px] border-b-1 border-[#E5E5E5]"
              >
                <input
                  v-model="replyCommentValue"
                  type="text"
                  class="w-full text-[14px] leading-[38px]"
                  placeholder="Reply a comment.."
                >
                <template v-if="replyCommentValue">
                  <div
                    class="h-[40px] leading-[38px] px-[16px] md:px-[24px] cursor-pointer"
                    @click="cancelReplyComment"
                  >
                    Cancel
                  </div>
                  <div
                    class="h-[40px] text-[#668AF1] leading-[38px] px-[16px] md:px-[24px] cursor-pointer border-1 border-[#668AF1] rounded-[40px]"
                    @click="submit(comment.id)"
                  >
                    Comment
                  </div>
                </template>
              </div>
              <div
                v-if="comment.replies_count"
                class="flex flex-col ml-[40px]"
              >
                <div
                  class="flex items-center gap-[4px] w-fit leading-none cursor-pointer"
                  @click="switchOpenReplies(comment.id)"
                >
                  <ChevronDownIcon
                    class="size-[12px]"
                    :class="{'rotate-180': openReplies[comment.id]}"
                  />
                  <div class="text-[12px]">
                    {{ comment.replies_count }} replies
                  </div>
                </div>
                <div
                  v-if="openReplies[comment.id]"
                  class="flex flex-col gap-[8px] mt-[8px]"
                >
                  <div
                    v-for="subComment in subComments[comment.id]"
                    :key="subComment.id"
                    class="flex"
                  >
                    <img
                      v-if="subComment.creator.avatar_url"
                      :src="subComment.creator.avatar_url"
                      class="size-[24px] mr-[8px] rounded-full"
                    >
                    <DefaultAvatar
                      v-else
                      class="size-[40px]"
                    />
                    <div class="flex-1 flex flex-col">
                      <div class="flex items-baseline gap-[4px] leading-none mb-[4px]">
                        <div class="font-bold">
                          {{ subComment.creator.full_name || 'Anonymous' }}
                        </div>
                        <div class="text-[#999999] text-[12px]">
                          {{ formatDate(subComment.created_at) }}
                        </div>
                      </div>
                      <div class="text-[14px] mb-[8px]">
                        {{ subComment.content }}
                      </div>
                      <div class="flex items-center gap-[6px] text-[#999999] text-[12px] leading-none">
                        <div
                          class="flex items-center gap-[5px] cursor-pointer"
                          @click="clickCommentLikeToggle(subComment)"
                        >
                          <HandThumbUpIconActive
                            v-if="subComment.is_like"
                            class="size-[12px]"
                          />
                          <HandThumbUpIcon
                            v-else
                            class="size-[12px]"
                          />
                          <div>{{ subComment.likes_count }}</div>
                        </div>
                      </div>
                    </div>
                    <div
                      v-if="subComment.creator.id === userStore.profile?.id"
                      class="ml-auto dropdown dropdown-end"
                    >
                      <div
                        tabindex="0"
                        role="button"
                        class="cursor-pointer"
                      >
                        <EllipsisVerticalIcon class="size-[24px] ml-auto" />
                      </div>
                      <ul
                        tabindex="0"
                        class="w-[174px] p-[4px] rounded-[8px] bg-white shadow-sm dropdown-content menu"
                      >
                        <li>
                          <div
                            class="p-[8px]"
                            @click="showDeleteCommentModal(subComment.id, subComment.parent_id)"
                          >
                            Delete
                          </div>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      class="modal-backdrop"
      @click="closeModal"
    />
  </dialog>
  <Modal
    v-if="removeConfig.id"
    :show="true"
    type="prompt"
    @close="closeDeleteCommentModal"
  >
    <div class="text-[20px] font-bold mb-[4px]">
      Delete this comment?
    </div>
    <div class="text-[14px] mb-[40px]">
      Are you sure you want to delete this comment? This action cannot be undone.
    </div>
    <div class="flex justify-end gap-[16px]">
      <div
        class="cursor-pointer py-[10px] px-[16px]"
        @click="closeDeleteCommentModal"
      >
        Cancel
      </div>
      <LoadingButton
        :loading="deleteLoading"
        class="text-white py-[10px] px-[16px] rounded-[40px] bg-[#EA3E3E]"
        @click="destory"
      >
        Delete
      </LoadingButton>
    </div>
  </Modal>
</template>

<style scoped>

</style>
