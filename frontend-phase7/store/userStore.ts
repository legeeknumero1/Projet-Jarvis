/**
 * Store Zustand pour la gestion de l'utilisateur
 */

'use client';

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { User, UserPreferences } from '@/types';

export interface UserState {
  // État
  user: User | null;
  isAuthenticated: boolean;
  token: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setAuthenticated: (isAuthenticated: boolean) => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
  logout: () => void;

  // Utils
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  resetStore: () => void;
}

const initialState = {
  user: null,
  isAuthenticated: false,
  token: null,
  isLoading: false,
  error: null,
};

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        setUser: (user) =>
          set({
            user,
            isAuthenticated: user !== null,
          }),

        setToken: (token) => set({ token }),

        setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),

        updatePreferences: (preferences) =>
          set((state) => {
            if (!state.user) return state;

            return {
              user: {
                ...state.user,
                preferences: {
                  ...state.user.preferences,
                  ...preferences,
                },
              },
            };
          }),

        logout: () => set(initialState),

        setLoading: (isLoading) => set({ isLoading }),

        setError: (error) => set({ error }),

        resetStore: () => set(initialState),
      }),
      {
        name: 'user-store',
        version: 1,
      },
    ),
  ),
);
