import { useMutation } from '@tanstack/vue-query';

import { uploadImage } from '@/services/tool';

export const useUploadImage = () => {
  return useMutation({
    mutationFn: (params: {formData: FormData, onProgress: ((progress: number) => void) | null}) => uploadImage(params.formData, params.onProgress),
  });
}
