export interface App {
  id: string;
  name: string | null;
  cover: string | null;
  category: AppCategory | null;
  icon?: string | null;
  description: string | null;
  page_view?: number;
  comments_count?: number;
  likes_count?: number;
  favorites_count?: number;
  created_at?: string;
  creator?: {
    id: string,
    avatar_url: string;
    full_name: string;
  };
  type?: 'bookmarked' | 'owned'
}

export interface AppDetail extends App {
  updated_at: string;
}

export interface AppComment {
  id: string;
  content: string;
  replies_count: number;
  creator: {
    id: string;
    avatar_url: string;
    full_name: string;
  };
  created_at: string;
  likes_count: number;
  is_like?: boolean;
}

export interface AppSubComment {
  id: string;
  content: string;
  creator: {
    id: string;
    avatar_url: string;
    full_name: string;
  };
  parent_id: string;
  created_at: string;
  likes_count: number;
  is_like?: boolean;
}

export interface AppCommunityDetail {
  id: string;
  name: string | null;
  cover: string | null;
  category: AppCategory | null;
  icon: string | null;
  description: string | null;
  page_view: number;
  likes_count: number;
  updated_at: string;
  creator: {
    id: string,
    avatar_url: string;
    full_name: string;
    followers_count: number;
  };
  bookmarks_count: number;
  has_bookmark?: boolean;
}

export const AppCategories = {
  productivity: 'Productivity',
  utility: 'Utility',
  work: 'Work',
  dating: 'Dating',
  health_fitness: 'Health & Fitness',
  education: 'Education',
  entertainment: 'Entertainment',
  finance: 'Finance',
  kids: 'Kids',
  lifestyle: 'Lifestyle',
  medical: 'Medical',
  photo_video: 'Photo & Video',
  social_networking: 'Social Networking',
  sports: 'Sports',
  travel: 'Travel',
  weather: 'Weather',
  games: 'Games',
  misc: 'Misc',
}

export type AppCategory = keyof typeof AppCategories;

export const enum AppStage {
  Default = 'default',
  Planning = 'planning',
  Building = 'building',
  Built = 'built',
  Deploying = 'deploying',
  Deployed = 'deployed',
  /**
   * @deprecated Use `Deployed` instead.
   */
  Testing = 'testing',
}

export interface ChatEvent {
  id: string;
  timestamp: string;
  role: 'user' | 'assistant';
  event: 'end' | 'error' | 'message' | 'plan' | 'progress' | 'tool_use';
  data: any;
}
