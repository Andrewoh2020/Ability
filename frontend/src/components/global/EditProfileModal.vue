<script setup lang="ts">
import { useModalStore } from '@/stores/modal';
import Modal from '@/components/Modal.vue';
import EditProfile from '@/components/EditProfile.vue';

const modalStore = useModalStore();

const handleClose = () => {
  modalStore.showEditProfile = false;
}
</script>

<template>
  <Modal ref="modalRef" :show="true" type="edit" @close="handleClose">
    <EditProfile @updated="handleClose" />
  </Modal>
</template>
