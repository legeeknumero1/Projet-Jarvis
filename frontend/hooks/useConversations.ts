import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { queryKeys } from '@/lib/query-client';

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

/**
 * Hook for fetching conversations list
 */
export function useConversations() {
  return useQuery({
    queryKey: queryKeys.chat.conversations(),
    queryFn: async () => {
      const response = await api.get<Conversation[]>('/api/chat/conversations');
      return response.data;
    },
    // Refetch every 30 seconds for real-time updates
    refetchInterval: 30000,
  });
}

/**
 * Hook for fetching conversation history
 */
export function useConversationHistory(conversationId: string) {
  return useQuery({
    queryKey: queryKeys.chat.history(conversationId),
    queryFn: async () => {
      const response = await api.get(`/api/chat/history/${conversationId}`);
      return response.data;
    },
    enabled: !!conversationId, // Only fetch if ID is provided
  });
}

/**
 * Hook for sending a chat message
 */
export function useSendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (message: string) => {
      const response = await api.post('/api/chat', { content: message });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate conversations to refetch latest
      queryClient.invalidateQueries({ queryKey: queryKeys.chat.conversations() });
    },
  });
}

/**
 * Hook for deleting a conversation
 */
export function useDeleteConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (conversationId: string) => {
      await api.delete(`/api/chat/conversation/${conversationId}`);
    },
    onSuccess: () => {
      // Invalidate and refetch conversations
      queryClient.invalidateQueries({ queryKey: queryKeys.chat.conversations() });
    },
  });
}
