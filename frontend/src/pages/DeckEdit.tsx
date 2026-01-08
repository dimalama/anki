import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Save } from 'lucide-react';
import { decksApi, cardsApi } from '../services/api';
import type { Deck, Card, CardCreate } from '../types';

export default function DeckEdit() {
  const { deckId } = useParams<{ deckId: string }>();
  const navigate = useNavigate();
  const [deck, setDeck] = useState<Deck | null>(null);
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [nextNewId, setNextNewId] = useState(-1);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (deckId) {
      loadDeck();
      loadCards();
    }
  }, [deckId]);

  const loadDeck = async () => {
    try {
      const response = await decksApi.get(deckId!);
      setDeck(response.deck || null);
    } catch (err) {
      setError('Failed to load deck');
    }
  };

  const loadCards = async () => {
    try {
      setLoading(true);
      const response = await cardsApi.list(deckId!);
      setCards(response.cards);
    } catch (err) {
      setError('Failed to load cards');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCard = () => {
    const fields: Record<string, string> = deck?.card_type === 'cloze'
      ? { Text: '', Translation: '', Explanation: '' }
      : { Front: '', Back: '' };

    const newCard: Card = {
      id: nextNewId,
      deck_id: deckId!,
      fields,
      tags: [],
    };
    setNextNewId(nextNewId - 1);
    setCards([...cards, newCard]);
  };

  const handleCardChange = (index: number, field: string, value: string) => {
    const updatedCards = [...cards];
    updatedCards[index].fields[field] = value;
    setCards(updatedCards);
  };

  const handleSave = async () => {
    try {
      // Separate existing cards (id >= 0) from new cards (id < 0)
      const existingCards = cards.filter(card => card.id >= 0);
      const newCards = cards.filter(card => card.id < 0);

      // Update existing cards
      for (const card of existingCards) {
        await cardsApi.update(deckId!, card.id, {
          fields: card.fields,
          tags: card.tags,
        });
      }

      // Create only new cards
      if (newCards.length > 0) {
        const newCardData: CardCreate[] = newCards.map(card => ({
          fields: card.fields,
          tags: card.tags,
        }));
        await cardsApi.createBatch(deckId!, newCardData);
      }

      alert('Deck saved successfully!');
      navigate('/');
    } catch (err) {
      alert('Failed to save deck');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading deck...</p>
        </div>
      </div>
    );
  }

  if (error || !deck) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-800 dark:text-red-200">{error || 'Deck not found'}</p>
      </div>
    );
  }

  const fieldNames = Object.keys(cards[0]?.fields || (deck.card_type === 'cloze'
    ? { Text: '', Translation: '', Explanation: '' }
    : { Front: '', Back: '' }));

  return (
    <div className="max-w-6xl mx-auto">
      <button
        onClick={() => navigate('/')}
        className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-6"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>Back to Dashboard</span>
      </button>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Edit Deck: {deck.name}
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {deck.card_count} cards • {deck.language} • {deck.card_type}
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleAddCard}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <Plus className="w-5 h-5" />
              <span>Add Card</span>
            </button>
            <button
              onClick={handleSave}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Save className="w-5 h-5" />
              <span>Save</span>
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {cards.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
              <p className="text-gray-600 dark:text-gray-400 mb-4">No cards yet</p>
              <button
                onClick={handleAddCard}
                className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Add First Card
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">#</th>
                    {fieldNames.map((field) => (
                      <th key={field} className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                        {field}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {cards.map((card, index) => (
                    <tr key={index} className="border-b border-gray-100 dark:border-gray-700">
                      <td className="p-3 text-gray-600 dark:text-gray-400">{index + 1}</td>
                      {fieldNames.map((field) => (
                        <td key={field} className="p-3">
                          <input
                            type="text"
                            value={card.fields[field] || ''}
                            onChange={(e) => handleCardChange(index, field, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                            placeholder={`Enter ${field.toLowerCase()}...`}
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
