export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url: string;
  bio?: string;
  birthday?: string;
  country?: string;
  city?: string;
  interests?: string[];
}

export interface UserCommunity {
  id: string;
  full_name: string;
  avatar_url: string;
  bio?: string;
  following_count: number;
  followers_count: number;
}

export interface UserConnection {
  id: string;
  full_name: string;
  avatar_url: string;
  followed_at: string;
  is_following?: boolean;
}
