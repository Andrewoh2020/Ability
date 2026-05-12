import { format, formatDistanceToNow } from 'date-fns';

import router from '@/router';

export function formatDate(dateString: string, formatType: string = 'relative') {
  const date = new Date(dateString);

  const formatMap: Record<string, string> = {
    'YYYY-MM-DD': 'yyyy-MM-dd',
    'YYYY/MM/DD': 'yyyy/MM/dd',
    'MM-DD': 'MM-dd',
    'HH:mm': 'HH:mm',
    'HH:mm:ss': 'HH:mm:ss',
    'YYYY-MM-DD HH:mm': 'yyyy-MM-dd HH:mm',
    'YYYY-MM-DD HH:mm:ss': 'yyyy-MM-dd HH:mm:ss',
    'relative': 'relative'
  };

  const formatStr = formatMap[formatType] || formatType;

  if (formatStr === 'relative') {
    return formatDistanceToNow(date, { addSuffix: true });
  }

  return format(date, formatStr);
}

export function closeDropdown() {
  (document.activeElement as HTMLElement)?.blur?.();
}

export function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return 'Just now';
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes}min ago`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours}hr ago`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  return `${diffInDays}d ago`;
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  } else {
    return num.toString()
  }
}

export function routerBack() {
  document.body.focus();

  const backPath = router.options.history.state.back;
  if (backPath && typeof backPath === 'string') {
    router.replace(backPath);
  } else {
    router.replace('/');
  }
}

export function uid(n = 8): string {
  return Math.random().toString(36).slice(2, n + 2);
}
