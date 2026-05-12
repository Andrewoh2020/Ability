export interface BaseResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface Message {
  id: string;
  timestamp: string;
  role: 'user' | 'assistant';
  type: 'message' | 'plan' | 'progress' | 'end' | 'error';
  data: any;
  htmlContent?: string;
  duration?: number;
}
