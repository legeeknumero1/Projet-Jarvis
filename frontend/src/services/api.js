const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8100';

export const apiService = {
  async login(username, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    return response.json();
  },

  async sendMessage(content, conversationId = null) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        content,
        conversation_id: conversationId,
      }),
    });
    return response.json();
  },

  async getHistory(conversationId) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/chat/history/${conversationId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  async getConversations() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/chat/conversations`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  }
};
