/**
 * Client API axios pour communiquer avec le backend Rust
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { AppError, ApiResponse, PaginatedResponse } from '@/types';

// Configuration du client API
const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Interceptor pour ajouter le token d'authentification
API.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Interceptor pour gérer les erreurs
API.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const message = error.response?.data ? JSON.stringify(error.response.data) : error.message;
    const statusCode = error.response?.status || 500;
    throw new AppError(
      'API_ERROR',
      `Erreur API: ${message}`,
      statusCode,
      error.response?.data,
    );
  },
);

// === Chat API ===
export const chatApi = {
  /**
   * Envoyer un message au backend
   */
  sendMessage: async (conversationId: string, content: string): Promise<ApiResponse<any>> => {
    const response = await API.post('/api/chat/message', {
      conversationId,
      content,
    });
    return response.data;
  },

  /**
   * Obtenir l'historique d'une conversation
   */
  getHistory: async (conversationId: string, limit: number = 50): Promise<any> => {
    const response = await API.get(`/api/chat/history/${conversationId}`, {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Créer une nouvelle conversation
   */
  createConversation: async (title: string): Promise<any> => {
    const response = await API.post('/api/chat/conversation', { title });
    return response.data;
  },

  /**
   * Obtenir la liste des conversations
   */
  listConversations: async (page: number = 1, limit: number = 20): Promise<PaginatedResponse<any>> => {
    const response = await API.get('/api/chat/conversations', {
      params: { page, limit },
    });
    return response.data;
  },

  /**
   * Archiver une conversation
   */
  archiveConversation: async (conversationId: string): Promise<ApiResponse<any>> => {
    const response = await API.post(`/api/chat/conversation/${conversationId}/archive`);
    return response.data;
  },

  /**
   * Supprimer une conversation
   */
  deleteConversation: async (conversationId: string): Promise<ApiResponse<any>> => {
    const response = await API.delete(`/api/chat/conversation/${conversationId}`);
    return response.data;
  },
};

// === User API ===
export const userApi = {
  /**
   * Obtenir les infos de l'utilisateur courant
   */
  getProfile: async (): Promise<any> => {
    const response = await API.get('/api/user/profile');
    return response.data;
  },

  /**
   * Mettre à jour les préférences utilisateur
   */
  updatePreferences: async (preferences: Record<string, unknown>): Promise<ApiResponse<any>> => {
    const response = await API.put('/api/user/preferences', preferences);
    return response.data;
  },

  /**
   * Obtenir les statistiques d'utilisation
   */
  getUsageStats: async (): Promise<any> => {
    const response = await API.get('/api/user/stats');
    return response.data;
  },
};

// === Plugins API ===
export const pluginsApi = {
  /**
   * Obtenir la liste des plugins disponibles
   */
  list: async (): Promise<any[]> => {
    const response = await API.get('/api/plugins');
    return response.data;
  },

  /**
   * Activer un plugin
   */
  enable: async (pluginId: string): Promise<ApiResponse<any>> => {
    const response = await API.post(`/api/plugins/${pluginId}/enable`);
    return response.data;
  },

  /**
   * Désactiver un plugin
   */
  disable: async (pluginId: string): Promise<ApiResponse<any>> => {
    const response = await API.post(`/api/plugins/${pluginId}/disable`);
    return response.data;
  },

  /**
   * Exécuter une commande de plugin
   */
  executeCommand: async (pluginId: string, command: string, args?: any): Promise<ApiResponse<any>> => {
    const response = await API.post(`/api/plugins/${pluginId}/command`, {
      command,
      args,
    });
    return response.data;
  },
};

// === Automations API ===
export const automationsApi = {
  /**
   * Obtenir la liste des automations
   */
  list: async (): Promise<any[]> => {
    const response = await API.get('/api/automations');
    return response.data;
  },

  /**
   * Créer une nouvelle automation
   */
  create: async (automation: any): Promise<ApiResponse<any>> => {
    const response = await API.post('/api/automations', automation);
    return response.data;
  },

  /**
   * Mettre à jour une automation
   */
  update: async (automationId: string, automation: any): Promise<ApiResponse<any>> => {
    const response = await API.put(`/api/automations/${automationId}`, automation);
    return response.data;
  },

  /**
   * Supprimer une automation
   */
  delete: async (automationId: string): Promise<ApiResponse<any>> => {
    const response = await API.delete(`/api/automations/${automationId}`);
    return response.data;
  },

  /**
   * Exécuter une automation manuellement
   */
  execute: async (automationId: string): Promise<ApiResponse<any>> => {
    const response = await API.post(`/api/automations/${automationId}/execute`);
    return response.data;
  },
};

// === Auth API ===
export const authApi = {
  /**
   * S'authentifier
   */
  login: async (email: string, password: string): Promise<any> => {
    const response = await API.post('/api/auth/login', { email, password });
    return response.data;
  },

  /**
   * Se déconnecter
   */
  logout: async (): Promise<ApiResponse<any>> => {
    const response = await API.post('/api/auth/logout');
    return response.data;
  },

  /**
   * S'enregistrer
   */
  register: async (email: string, password: string, name: string): Promise<any> => {
    const response = await API.post('/api/auth/register', {
      email,
      password,
      name,
    });
    return response.data;
  },

  /**
   * Rafraîchir le token
   */
  refreshToken: async (): Promise<any> => {
    const response = await API.post('/api/auth/refresh');
    return response.data;
  },
};

// === Health API ===
export const healthApi = {
  /**
   * Vérifier la santé de l'API
   */
  check: async (): Promise<any> => {
    const response = await API.get('/health');
    return response.data;
  },

  /**
   * Vérifier la santé d'un service spécifique
   */
  checkService: async (serviceName: string): Promise<any> => {
    const response = await API.get(`/health/${serviceName}`);
    return response.data;
  },
};

export default API;
