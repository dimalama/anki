// TypeScript types for the application

export interface Deck {
  id: string;
  name: string;
  language: string;
  description?: string;
  tags: string[];
  card_type: 'basic' | 'cloze' | 'reversed';
  card_count: number;
  created_at?: string;
  updated_at?: string;
  csv_path: string;
  apkg_path?: string;
}

export interface DeckCreate {
  name: string;
  language: string;
  description?: string;
  tags: string[];
  card_type: 'basic' | 'cloze' | 'reversed';
}

export interface DeckUpdate {
  name?: string;
  language?: string;
  description?: string;
  tags?: string[];
}

export interface Card {
  id: number;
  deck_id: string;
  fields: Record<string, string>;
  tags: string[];
}

export interface CardCreate {
  fields: Record<string, string>;
  tags: string[];
}

export interface CardUpdate {
  fields?: Record<string, string>;
  tags?: string[];
}

export interface Template {
  id: string;
  name: string;
  type: 'basic' | 'cloze';
  qfmt: string;
  afmt: string;
  css?: string;
  is_default: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface DeckResponse {
  success: boolean;
  message: string;
  deck?: Deck;
}

export interface DeckListResponse {
  success: boolean;
  count: number;
  decks: Deck[];
}

export interface CardListResponse {
  success: boolean;
  count: number;
  cards: Card[];
}

export interface TemplateListResponse {
  success: boolean;
  count: number;
  templates: Template[];
}
