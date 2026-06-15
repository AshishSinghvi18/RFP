import { get, post, TOKEN_STORAGE_KEY, USER_STORAGE_KEY } from '@/services/api';
import type { TokenResponse, UserResponse } from '@/utils/types';

const persistSession = (session: TokenResponse) => {
  localStorage.setItem(TOKEN_STORAGE_KEY, session.token);
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(session.user));
};

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const session = await post<TokenResponse>('/auth/login', { email, password });
  persistSession(session);
  return session;
};

export const getCurrentUser = async (): Promise<UserResponse> => {
  const user = await get<UserResponse>('/auth/me');
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  return user;
};

export const logout = () => {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
};

export const isAuthenticated = () => Boolean(localStorage.getItem(TOKEN_STORAGE_KEY));
