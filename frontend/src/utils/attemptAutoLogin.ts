import { useUserStore } from "@/stores/user";
import { refreshToken } from "@/services/auth";

let attemptAutoLoginPromise: Promise<void> | null = null;

const attemptAutoLogin = (): Promise<void> => {
  if (attemptAutoLoginPromise) {
    return attemptAutoLoginPromise;
  }

  attemptAutoLoginPromise = (async () => {
    const token = localStorage.getItem('refresh_token');
    if (!token) throw new Error('No refresh token');

    const userStore = useUserStore();
    const data = await refreshToken(token);
    userStore.login(data.access_token, data.refresh_token);
  })().catch((error) => {
    const userStore = useUserStore();
    userStore.clean();
    throw error;
  }).finally(() => {
    attemptAutoLoginPromise = null;
  });

  return attemptAutoLoginPromise;
};


export {
  attemptAutoLogin,
  attemptAutoLoginPromise,
}
