// API client for backend communication

import axios from 'axios';
import type {
  Deck,
  DeckCreate,
  DeckUpdate,
  DeckListResponse,
  DeckResponse,
  Card,
  CardCreate,
  CardUpdate,
  CardListResponse,
  Template,
  TemplateListResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Decks API
export const decksApi = {
  list: async (language?: string, tag?: string): Promise<DeckListResponse> => {
    const params = new URLSearchParams();
    if (language) params.append('language', language);
    if (tag) params.append('tag', tag);
    const response = await api.get(`/decks?${params.toString()}`);
    return response.data;
  },

  get: async (deckId: string): Promise<DeckResponse> => {
    const response = await api.get(`/decks/${deckId}`);
    return response.data;
  },

  create: async (deckData: DeckCreate): Promise<DeckResponse> => {
    const response = await api.post('/decks', deckData);
    return response.data;
  },

  update: async (deckId: string, deckData: DeckUpdate): Promise<DeckResponse> => {
    const response = await api.put(`/decks/${deckId}`, deckData);
    return response.data;
  },

  delete: async (deckId: string): Promise<DeckResponse> => {
    const response = await api.delete(`/decks/${deckId}`);
    return response.data;
  },

  generate: async (deckId: string): Promise<DeckResponse> => {
    const response = await api.post(`/decks/${deckId}/generate`);
    return response.data;
  },

  download: async (deckId: string): Promise<Blob> => {
    const response = await api.get(`/decks/${deckId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Cards API
export const cardsApi = {
  list: async (deckId: string): Promise<CardListResponse> => {
    const response = await api.get(`/cards/${deckId}/cards`);
    return response.data;
  },

  create: async (deckId: string, cardData: CardCreate): Promise<Card> => {
    const response = await api.post(`/cards/${deckId}/cards`, cardData);
    return response.data.card;
  },

  createBatch: async (deckId: string, cards: CardCreate[]): Promise<CardListResponse> => {
    const response = await api.post(`/cards/${deckId}/cards/batch`, { cards });
    return response.data;
  },

  update: async (deckId: string, cardId: number, cardData: CardUpdate): Promise<Card> => {
    const response = await api.put(`/cards/${deckId}/cards/${cardId}`, cardData);
    return response.data.card;
  },

  delete: async (deckId: string, cardId: number): Promise<void> => {
    await api.delete(`/cards/${deckId}/cards/${cardId}`);
  },
};

// Templates API
export const templatesApi = {
  list: async (): Promise<TemplateListResponse> => {
    const response = await api.get('/templates');
    return response.data;
  },

  get: async (templateId: string): Promise<Template> => {
    const response = await api.get(`/templates/${templateId}`);
    return response.data.template;
  },
};

// Import API
export const importApi = {
  fromCSV: async (file: File, deckName?: string, language = 'spanish', cardType = 'basic'): Promise<DeckResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (deckName) formData.append('deck_name', deckName);
    formData.append('language', language);
    formData.append('card_type', cardType);

    const response = await api.post('/import/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  fromText: async (
    text: string,
    deckName: string,
    language = 'spanish',
    separator = '\t',
    cardType = 'basic'
  ): Promise<DeckResponse> => {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('deck_name', deckName);
    formData.append('language', language);
    formData.append('separator', separator);
    formData.append('card_type', cardType);

    const response = await api.post('/import/text', formData);
    return response.data;
  },
};

export default api;
