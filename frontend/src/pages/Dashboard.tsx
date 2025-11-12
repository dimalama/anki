import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Download, Edit, Trash2, FileText } from 'lucide-react';
import { decksApi } from '../services/api';
import type { Deck } from '../types';

export default function Dashboard() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDecks();
  }, []);

  const loadDecks = async () => {
    try {
      setLoading(true);
      const response = await decksApi.list();
      setDecks(response.decks);
      setError(null);
    } catch (err) {
      setError('Failed to load decks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (deckId: string, deckName: string) => {
    try {
      // First generate the deck
      await decksApi.generate(deckId);

      // Then download it
      const blob = await decksApi.download(deckId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${deckId}.apkg`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading deck:', err);
      alert('Failed to download deck');
    }
  };

  const handleDelete = async (deckId: string) => {
    if (!confirm('Are you sure you want to delete this deck?')) {
      return;
    }

    try {
      await decksApi.delete(deckId);
      loadDecks(); // Reload the list
    } catch (err) {
      console.error('Error deleting deck:', err);
      alert('Failed to delete deck');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading decks...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-800 dark:text-red-200">{error}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Your Decks
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Manage and create Anki flashcard decks
        </p>
      </div>

      {decks.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No decks yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Get started by creating your first deck or importing one
          </p>
          <div className="flex justify-center space-x-4">
            <Link
              to="/decks/create"
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              Create New Deck
            </Link>
            <Link
              to="/import"
              className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              Import Deck
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {decks.map((deck) => (
            <div
              key={deck.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {deck.name}
                  </h3>
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="px-2 py-1 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 text-xs rounded">
                      {deck.language}
                    </span>
                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs rounded">
                      {deck.card_type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                    <FileText className="w-4 h-4 mr-1" />
                    {deck.card_count} cards
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-1 mb-4">
                {deck.tags.slice(0, 4).map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded"
                  >
                    #{tag}
                  </span>
                ))}
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => handleDownload(deck.id, deck.name)}
                  className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition"
                  title="Download .apkg file"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>

                <Link
                  to={`/decks/${deck.id}/edit`}
                  className="flex items-center justify-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 text-sm rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                  title="Edit deck"
                >
                  <Edit className="w-4 h-4" />
                </Link>

                <button
                  onClick={() => handleDelete(deck.id)}
                  className="flex items-center justify-center px-3 py-2 border border-red-300 dark:border-red-600 text-red-700 dark:text-red-400 text-sm rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition"
                  title="Delete deck"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
