# 🌐 Jarvis Frontend Phase 7 - TypeScript (React + Next.js Upgrade)

**Frontend moderne en React 19 + TypeScript + Next.js 14 + ShadCN UI**

Migration vers Next.js avec architecture modulaire, type-safe et performance-optimized.

---

## 🎯 Architecture

### Stack Technique

- **Next.js 14** : App Router, Server Components, Streaming
- **React 19** : Nouvelles features, meilleures performances
- **TypeScript** : Type-safety strict
- **ShadCN UI** : Composants Radix UI + Tailwind
- **Zustand** : State management léger
- **React Hook Form** : Formulaires performants

---

## 📂 Structure

```
frontend-phase7/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   ├── (chat)/
│   │   ├── layout.tsx          # Chat layout
│   │   ├── page.tsx            # Chat page
│   │   └── [id]/page.tsx       # Conversation detail
│   ├── (dashboard)/
│   │   ├── page.tsx            # Dashboard
│   │   ├── automations/        # Automations management
│   │   ├── settings/           # User settings
│   │   └── analytics/          # Usage analytics
│   └── api/
│       ├── chat/route.ts       # Chat API route
│       └── health/route.ts     # Health check
├── components/
│   ├── chat/
│   │   ├── MessageList.tsx
│   │   ├── MessageInput.tsx
│   │   ├── ConversationList.tsx
│   │   └── ChatLayout.tsx
│   ├── dashboard/
│   │   ├── ServiceStatus.tsx
│   │   ├── MetricsChart.tsx
│   │   └── AutomationCard.tsx
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Dialog.tsx
│   │   └── ... (ShadCN components)
│   └── common/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── hooks/
│   ├── useChat.ts
│   ├── useWebSocket.ts
│   ├── useHealth.ts
│   └── useAutomations.ts
├── lib/
│   ├── api.ts                  # API client
│   ├── types.ts                # TypeScript types
│   ├── constants.ts            # Constants
│   └── utils.ts                # Utilities
├── styles/
│   ├── globals.css
│   └── variables.css
├── store/
│   ├── chatStore.ts            # Chat state (Zustand)
│   ├── uiStore.ts              # UI state
│   └── settingsStore.ts        # Settings state
├── next.config.js
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

---

## 🎨 Key Components

### ChatLayout
```tsx
export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <Header />
        {children}
      </main>
    </div>
  );
}
```

### MessageList
```tsx
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tokens?: number;
}

export function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div className="flex-1 overflow-y-auto space-y-4 p-4">
      {messages.map((msg) => (
        <MessageItem key={msg.id} message={msg} />
      ))}
    </div>
  );
}
```

### useChat Hook
```tsx
export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (content: string) => {
    setIsLoading(true);
    try {
      const response = await api.post('/api/chat', { content });
      setMessages(prev => [...prev, response.data]);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, sendMessage };
}
```

---

## 🔌 API Integration

### Client API
```tsx
// lib/api.ts
import axios from 'axios';

const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100',
});

export const chatApi = {
  sendMessage: (message: string) =>
    API.post('/api/chat', { content: message }),

  getHistory: (conversationId: string) =>
    API.get(`/api/chat/history/${conversationId}`),

  listConversations: () =>
    API.get('/api/chat/conversations'),
};

export const healthApi = {
  check: () => API.get('/health'),
  getMetrics: () => API.get('/metrics'),
};
```

### WebSocket Integration
```tsx
export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => setIsConnected(true);
    ws.onmessage = (e) => setLastMessage(JSON.parse(e.data));
    ws.onclose = () => setIsConnected(false);

    wsRef.current = ws;
    return () => ws.close();
  }, [url]);

  return { isConnected, lastMessage };
}
```

---

## 🎯 State Management (Zustand)

```tsx
// store/chatStore.ts
interface ChatState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];

  setCurrentConversation: (conv: Conversation) => void;
  addMessage: (msg: Message) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  currentConversation: null,
  messages: [],

  setCurrentConversation: (conv) =>
    set({ currentConversation: conv }),

  addMessage: (msg) =>
    set((state) => ({
      messages: [...state.messages, msg],
    })),

  clearChat: () =>
    set({ messages: [], currentConversation: null }),
}));
```

---

## 🔒 Security Features

- ✅ **Type-safety** : TypeScript strict mode
- ✅ **CSRF Protection** : Next.js built-in
- ✅ **XSS Prevention** : React automatic escaping
- ✅ **Secure Headers** : Via Next.js middleware
- ✅ **API Authentication** : Bearer token support
- ✅ **Input Validation** : Zod schemas

---

## 📊 Performance Optimizations

- ✅ **Server Components** : Reduce JS bundle
- ✅ **Image Optimization** : Next.js Image component
- ✅ **Code Splitting** : Dynamic imports
- ✅ **Caching** : ISR (Incremental Static Regeneration)
- ✅ **CSS-in-JS** : Tailwind with purging
- ✅ **Bundle Analysis** : Built-in reporting

---

## 🚀 Deployment

### Docker
```dockerfile
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables
```
NEXT_PUBLIC_API_URL=http://localhost:8100
NEXT_PUBLIC_WS_URL=ws://localhost:8100/ws
NEXT_PUBLIC_OLLAMA_URL=http://localhost:11434
```

---

## 🤝 Intégration Architecture

**Phase 7 dans l'architecture :**
- ✅ Phase 1-6: Core infrastructure
- 🌐 Phase 7: **Frontend TypeScript** (YOU ARE HERE)
- 🧩 Phase 8: Lua Plugins
- ☁️ Phase 9: Elixir HA

---

**🌐 Jarvis Frontend - Type-safe, performant, modern UI**

*Architecture Polyglotte Phase 7*
