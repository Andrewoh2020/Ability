<script setup lang="ts">
import { ref } from 'vue';

import { useUserStore } from '@/stores/user';
import { useModalStore } from '@/stores/modal';
import { useGetUserProfile } from '@/composables/user';

import Modal from '@/components/Modal.vue';
import Login from '@/components/Login.vue';

const modalRef = ref();
const userStore = useUserStore();
const modalStore = useModalStore();
const { refetch } = useGetUserProfile(false);

const handleLogined = async () => {
  const { data } = await refetch();
  userStore.profile = data!;
  modalRef.value?.closeModal();
}

const handleClose = () => {
  modalStore.showLogin = false;
}
</script>

<template>
  <Modal
    ref="modalRef"
    :show="true"
    type="login"
    class="z-[1000]"
    @close="handleClose"
  >
    <Login @logined="handleLogined" />
  </Modal>
</template>

<style scoped>

</style>
