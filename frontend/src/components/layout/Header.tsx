import { Link } from 'react-router-dom';
import { BookOpen, Plus, Upload } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-white dark:bg-gray-800 shadow">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <BookOpen className="w-8 h-8 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Anki Deck Generator
            </h1>
          </Link>

          <nav className="flex items-center space-x-4">
            <Link
              to="/decks/create"
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              <Plus className="w-5 h-5" />
              <span>New Deck</span>
            </Link>

            <Link
              to="/import"
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              <Upload className="w-5 h-5" />
              <span>Import</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
