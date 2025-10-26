import { z } from 'zod';
import { publicProcedure, router } from '../trpc';

export const appRouter = router({
  // Chat procedures
  chat: {
    send: publicProcedure
      .input(z.object({ content: z.string() }))
      .mutation(async ({ input }) => {
        const response = await fetch('http://localhost:8100/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(input),
        });
        return response.json();
      }),

    getConversations: publicProcedure.query(async () => {
      const response = await fetch('http://localhost:8100/api/chat/conversations');
      return response.json();
    }),

    getHistory: publicProcedure
      .input(z.object({ conversationId: z.string() }))
      .query(async ({ input }) => {
        const response = await fetch(
          `http://localhost:8100/api/chat/history/${input.conversationId}`
        );
        return response.json();
      }),

    deleteConversation: publicProcedure
      .input(z.object({ conversationId: z.string() }))
      .mutation(async ({ input }) => {
        await fetch(`http://localhost:8100/api/chat/conversation/${input.conversationId}`, {
          method: 'DELETE',
        });
        return { success: true };
      }),
  },

  // Voice procedures
  voice: {
    synthesize: publicProcedure
      .input(z.object({ text: z.string(), language: z.string().optional() }))
      .mutation(async ({ input }) => {
        const response = await fetch('http://localhost:8100/api/voice/synthesize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(input),
        });
        return response.json();
      }),

    transcribe: publicProcedure
      .input(z.object({ audioData: z.string() }))
      .mutation(async ({ input }) => {
        const response = await fetch('http://localhost:8100/api/voice/transcribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(input),
        });
        return response.json();
      }),
  },

  // Memory procedures
  memory: {
    search: publicProcedure
      .input(z.object({ query: z.string(), limit: z.number().optional() }))
      .query(async ({ input }) => {
        const response = await fetch(
          `http://localhost:8100/api/memory/search?q=${input.query}&limit=${input.limit || 10}`
        );
        return response.json();
      }),

    store: publicProcedure
      .input(
        z.object({
          conversationId: z.string(),
          userMessage: z.string(),
          botResponse: z.string(),
        })
      )
      .mutation(async ({ input }) => {
        const response = await fetch('http://localhost:8100/api/memory/store', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(input),
        });
        return response.json();
      }),
  },

  // Health check
  health: publicProcedure.query(async () => {
    const response = await fetch('http://localhost:8100/health');
    return response.json();
  }),
});

export type AppRouter = typeof appRouter;
