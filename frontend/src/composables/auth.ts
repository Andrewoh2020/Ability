import { useMutation } from '@tanstack/vue-query';

import { magiclinkLogin, googleLogin } from '@/services/auth';

export const useMagiclinkLogin = () => {
  return useMutation({
    mutationFn: (email: string) => magiclinkLogin(email),
  });
}

export const useGoogleLogin = () => {
  return useMutation({
    mutationFn: (code: string) => googleLogin(code),
  });
}
