import axios from 'axios';

import { toast } from './toast';
import { useModalStore } from '@/stores/modal';
import { attemptAutoLogin, attemptAutoLoginPromise } from './attemptAutoLogin';

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 300000,
});

http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

let failedQueue: Array<{ resolve: (value: any) => void; config: any }> = [];
http.interceptors.response.use(
  (response) => {
    const { code, message } = response.data;
    if (code !== 0) {
      if (message) {
        toast.error(message);
      }
      throw new Error(message || 'Request Failed');
    } else {
      return response;
    }
  },
  async (error) => {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      toast.error('Request Timeout');
    } else if (error.response?.status >= 500) {
      toast.error('Server Error');
    } else if (error.response?.status === 401) {
      if (!error.config._retry) {
        if (attemptAutoLoginPromise) {
          // 如果正在刷新，把请求加入队列
          return new Promise((resolve) => {
            failedQueue.push({ resolve, config: error.config });
          });
        }
        try {
          await attemptAutoLogin();
          // 重试所有失败的请求
          failedQueue.forEach(({ resolve, config }) => {
            config._retry = true;
            resolve(http(config));
          });
          // 重试原始请求
          error.config._retry = true;
          return http(error.config);
        } catch (_error) {
          const modalStore = useModalStore();
          modalStore.showLogin = true;
        } finally {
          failedQueue = [];
        }
      }
      // toast.error('Unauthorized');
    } else if (error.response?.status === 404) {
      toast.error('Not Found');
    } else if (error.response?.status === 422) {
      toast.error('Bad Request');
    } else {
      toast.error('Network Error');
    }
    return Promise.reject(error);
  }
);

export default http;
