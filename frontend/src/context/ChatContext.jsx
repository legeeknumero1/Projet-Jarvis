import React, { createContext, useContext, useReducer } from 'react';

// Actions du contexte chat
const CHAT_ACTIONS = {
  ADD_MESSAGE: 'ADD_MESSAGE',
  CLEAR_MESSAGES: 'CLEAR_MESSAGES',
  SET_LOADING: 'SET_LOADING',
  SET_CONNECTED: 'SET_CONNECTED',
  SET_LISTENING: 'SET_LISTENING'
};

// État initial
const initialState = {
  messages: [],
  isLoading: false,
  isConnected: false,
  isListening: false
};

// Reducer pour gérer l'état
const chatReducer = (state, action) => {
  switch (action.type) {
    case CHAT_ACTIONS.ADD_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, action.payload]
      };
    
    case CHAT_ACTIONS.CLEAR_MESSAGES:
      return {
        ...state,
        messages: []
      };
    
    case CHAT_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };
    
    case CHAT_ACTIONS.SET_CONNECTED:
      return {
        ...state,
        isConnected: action.payload
      };
    
    case CHAT_ACTIONS.SET_LISTENING:
      return {
        ...state,
        isListening: action.payload
      };
    
    default:
      return state;
  }
};

// Création du contexte
const ChatContext = createContext();

// Hook pour utiliser le contexte
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

// Provider du contexte
export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  
  // Actions helpers
  const actions = {
    addMessage: (message) => dispatch({ 
      type: CHAT_ACTIONS.ADD_MESSAGE, 
      payload: message 
    }),
    
    clearMessages: () => dispatch({ 
      type: CHAT_ACTIONS.CLEAR_MESSAGES 
    }),
    
    setLoading: (loading) => dispatch({ 
      type: CHAT_ACTIONS.SET_LOADING, 
      payload: loading 
    }),
    
    setConnected: (connected) => dispatch({ 
      type: CHAT_ACTIONS.SET_CONNECTED, 
      payload: connected 
    }),
    
    setListening: (listening) => dispatch({ 
      type: CHAT_ACTIONS.SET_LISTENING, 
      payload: listening 
    })
  };

  return (
    <ChatContext.Provider value={{ state, actions }}>
      {children}
    </ChatContext.Provider>
  );
};