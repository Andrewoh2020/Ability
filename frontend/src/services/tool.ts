import http from '@/utils/http';
import { BaseResponse } from '@/types';

export async function uploadImage(
  formData: FormData,
  onProgress: ((progress: number) => void) | null = null,
) {
  const response = await http.post<BaseResponse<{ url: string }>>(
    '/upload/image',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    }
  );
  return response.data.data.url;
}
