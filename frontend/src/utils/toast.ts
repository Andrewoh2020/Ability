import { createApp } from 'vue';
import Toast from '@/components/global/Toast.vue';

let toastInstance: any = null;
let toastContainer: any = null;
const showToast = (options: ToastOptions) => {
  if (toastInstance) closeToast();

  toastContainer = document.createElement('div');
  document.body.appendChild(toastContainer);

  toastInstance = createApp(Toast, {
    ...options,
    onClose: closeToast
  });

  toastInstance.mount(toastContainer);
}

const closeToast = () => {
  if (!toastInstance) return;
  toastInstance.unmount();
  document.body.removeChild(toastContainer);
  toastInstance = null;
}

interface ToastExtraOptions {
  timer?: number;
  active?: boolean;
}

interface ToastOptions extends ToastExtraOptions {
  type: 'info' | 'success' | 'warning' | 'error';
  msg: string;
}

const toast = {
  success: (msg: string, options?: ToastExtraOptions) => showToast({ type: 'success', msg, ...options }),
  error: (msg: string, options?: ToastExtraOptions) => showToast({ type: 'error', msg, ...options }),
  info: (msg: string, options?: ToastExtraOptions) => showToast({ type: 'info', msg, ...options }),
  warning: (msg: string, options?: ToastExtraOptions) => showToast({ type: 'warning', msg, ...options }),
  closeToast: closeToast
}

export {
  toast,
  closeToast,
  type ToastOptions,
}
