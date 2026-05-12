<script setup lang="ts">
import { computed, ref, shallowRef, onMounted } from 'vue';
import { ArrowLeftIcon } from '@heroicons/vue/24/outline';

import { useUserStore } from '@/stores/user';
import { useMagiclinkLogin, useGoogleLogin } from '@/composables/auth';

import LoadingButton from '@/components/LoadingButton.vue';
import { toast } from '@/utils/toast';

const email = ref('');
const confirm = ref(false);
const googleClient = shallowRef<any>(null);
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
const { mutateAsync: magiclinkLogin, isPending: loading } = useMagiclinkLogin();
const { mutateAsync: googleLogin } = useGoogleLogin();

const emit = defineEmits<{
  'logined': [];
}>();

const validateEmail = computed(() => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value);
});

const submit = async () => {
  await magiclinkLogin(email.value);
  confirm.value = true;
}

const back = () => {
  email.value = '';
  confirm.value = false;
}

const loadGoogleScript = () => {
  return new Promise<void>((resolve) => {
    if (! document.querySelector('#google-auth')) {
      const script = document.createElement('script')
      script.id = 'google-auth';
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => {
        resolve();
      };
      document.body.appendChild(script);
    } else {
      resolve();
    }
  })
}

const initializeGoogleLogin = async () => {
  await loadGoogleScript();
  const google = (window as any).google;
  googleClient.value = google.accounts.oauth2.initCodeClient({
    client_id: googleClientId,
    scope: 'openid email profile',
    ux_mode: 'popup',
    callback: (response: { code: string }) => {
      submitGoogleLogin(response.code);
    },
    error_callback: (error: { type: string }) => {
      if (error.type === 'popup_failed_to_open') {
        toast.error('Please allow popups for this site');
      } else if (error.type === 'popup_closed') {
      }
    }
  });
}

const submitGoogleLogin = async (code: string) => {
  const data = await googleLogin(code);
  const userStore = useUserStore();
  userStore.login(data.access_token, data.refresh_token);
  emit('logined');
}

const tiggerGoogleButton = () => {
  if (googleClient.value) {
    googleClient.value.requestCode();
  }
}

onMounted(() => {
  initializeGoogleLogin();
})
</script>

<template>
  <template v-if="confirm">
    <img
      src="@/assets/email.png"
      class="size-[48px] mx-auto mb-[40px]"
    >
    <div class="flex flex-col items-center gap-[24px]">
      <div class="text-[32px] font-bold">
        Check your email
      </div>
      <div class="text-center">
        We emailed a magic link to <span class="font-bold">{{ email }}</span><p>Click the link to login or sign up</p>
      </div>
      <div
        class="flex items-center gap-[4px] cursor-pointer"
        @click="back"
      >
        <ArrowLeftIcon class="size-[16px]" />
        <div>Back</div>
      </div>
    </div>
  </template>
  <template v-else>
    <h3 class="text-[28px] md:text-[32px] font-bold text-center mb-[16px]">
      Welcome to Ability
    </h3>
    <p class="text-center mb-[40px]">
      Start building your app today
    </p>
    <button
      class="flex justify-center items-center gap-[8px] w-full cursor-pointer py-[16px] border-1 rounded-[40px] btn"
      :disabled="!googleClient || loading"
      @click="tiggerGoogleButton"
    >
      <img
        src="@/assets/google-logo.png"
        class="w-[24px]"
      >
      <div class="text-[20px]">
        Continue with Google
      </div>
    </button>
    <p class="text-center my-[24px]">
      Or
    </p>
    <input
      v-model="email"
      type="email"
      class="w-full text-[20px] p-[16px] mb-[16px] rounded-[40px] input"
      :disabled="loading"
      placeholder="Enter email"
      required
    >
    <LoadingButton
      class="w-full text-[20px] py-[15px] rounded-[40px] btn-neutral"
      :loading="loading"
      :disable="!validateEmail"
      @click="submit"
    >
      Send magic link
    </LoadingButton>
  </template>
</template>

<style>
</style>
