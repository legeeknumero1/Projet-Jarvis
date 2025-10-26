import { QueryClient } from '@tanstack/react-query';

/**
 * TanStack Query Client Configuration
 * Optimized for Jarvis real-time chat and API interactions
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: 5 minutes for most queries
      staleTime: 5 * 60 * 1000,

      // Cache time: 10 minutes
      gcTime: 10 * 60 * 1000,

      // Retry failed requests 3 times with exponential backoff
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

      // Refetch on window focus for real-time updates
      refetchOnWindowFocus: true,

      // Refetch on reconnect
      refetchOnReconnect: true,

      // Don't refetch on mount if data is fresh
      refetchOnMount: false,
    },
    mutations: {
      // Retry mutations once on failure
      retry: 1,
      retryDelay: 1000,
    },
  },
});

/**
 * Query Keys for type-safe query management
 */
export const queryKeys = {
  // Chat queries
  chat: {
    all: ['chat'] as const,
    conversations: () => [...queryKeys.chat.all, 'conversations'] as const,
    history: (id: string) => [...queryKeys.chat.all, 'history', id] as const,
    messages: (conversationId: string) =>
      [...queryKeys.chat.all, 'messages', conversationId] as const,
  },

  // Voice queries
  voice: {
    all: ['voice'] as const,
    voices: () => [...queryKeys.voice.all, 'voices'] as const,
    languages: () => [...queryKeys.voice.all, 'languages'] as const,
  },

  // Memory queries
  memory: {
    all: ['memory'] as const,
    list: () => [...queryKeys.memory.all, 'list'] as const,
    search: (query: string) => [...queryKeys.memory.all, 'search', query] as const,
  },

  // Auth queries
  auth: {
    all: ['auth'] as const,
    whoami: () => [...queryKeys.auth.all, 'whoami'] as const,
  },
} as const;
