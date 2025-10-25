/**
 * Types partagés pour l'application Jarvis Frontend
 */

// Messages et conversations
export interface Message {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tokens?: number;
  metadata?: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  userId: string;
  title: string;
  summary?: string;
  messageCount: number;
  isArchived: boolean;
  createdAt: Date;
  updatedAt: Date;
  lastMessage?: Message;
}

export interface ChatRequest {
  conversationId?: string;
  message: string;
  context?: Record<string, unknown>;
}

export interface ChatResponse {
  conversationId: string;
  message: Message;
  success: boolean;
  error?: string;
}

// Utilisateur
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'user' | 'admin';
  createdAt: Date;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  emailNotifications: boolean;
  apiKey?: string;
}

// Authentification
export interface AuthResponse {
  token: string;
  user: User;
  expiresIn: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

// Plugins
export interface PluginMetadata {
  id: string;
  name: string;
  version: string;
  author: string;
  description: string;
  enabled: boolean;
}

export interface PluginCommand {
  name: string;
  description: string;
  args?: Record<string, unknown>;
}

// Automations
export interface Automation {
  id: string;
  name: string;
  enabled: boolean;
  triggers: AutomationTrigger[];
  conditions: AutomationCondition[];
  actions: AutomationAction[];
  createdAt: Date;
}

export type AutomationTrigger =
  | { type: 'time'; hour: number; minute: number }
  | { type: 'state_change'; entityId: string; from: string; to: string }
  | { type: 'motion'; entityId: string }
  | { type: 'webhook'; webhookId: string };

export type AutomationCondition =
  | { type: 'time_range'; start: string; end: string }
  | { type: 'state'; entityId: string; state: string }
  | { type: 'temperature'; entityId: string; threshold: number; operator: 'above' | 'below' };

export type AutomationAction =
  | { type: 'light'; entityId: string; action: 'on' | 'off'; brightness?: number }
  | { type: 'temperature'; entityId: string; temperature: number }
  | { type: 'notification'; title: string; message: string }
  | { type: 'mqtt'; topic: string; payload: string };

// API Responses
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: Date;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// WebSocket messages
export interface WebSocketMessage {
  type: 'chat' | 'typing' | 'status' | 'error' | 'notification';
  payload: unknown;
  timestamp: Date;
}

export interface ChatWebSocketMessage extends WebSocketMessage {
  type: 'chat';
  payload: {
    message: Message;
    conversationId: string;
  };
}

export interface TypingWebSocketMessage extends WebSocketMessage {
  type: 'typing';
  payload: {
    userId: string;
    isTyping: boolean;
  };
}

// Errors
export class AppError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number = 500,
    public details?: unknown,
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export interface ValidationError {
  field: string;
  message: string;
}

// Form data
export interface MessageFormData {
  content: string;
}

export interface ConversationFormData {
  title: string;
  summary?: string;
}
