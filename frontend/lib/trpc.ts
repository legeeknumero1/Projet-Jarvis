import { createTRPCReact } from '@trpc/react-query';
import { httpBatchLink } from '@trpc/client';
import type { AppRouter } from '@/server/routers/_app';
import superjson from 'superjson';

export const trpc = createTRPCReact<AppRouter>();

export const trpcClient = trpc.createClient({
  links: [
    httpBatchLink({
      url: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100/api/trpc',
      headers() {
        const token = typeof window !== 'undefined'
          ? localStorage.getItem('jarvis_token')
          : null;

        return token ? { authorization: `Bearer ${token}` } : {};
      },
    }),
  ],
  transformer: superjson,
});
