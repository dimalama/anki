import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, FileText } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { importApi } from '../services/api';

export default function Import() {
  const navigate = useNavigate();
  const [importType, setImportType] = useState<'csv' | 'text'>('csv');
  const [textData, setTextData] = useState('');
  const [deckName, setDeckName] = useState('');
  const [language, setLanguage] = useState('spanish');
  const [cardType, setCardType] = useState<'basic' | 'cloze'>('basic');
  const [separator, setSeparator] = useState('\t');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const response = await importApi.fromCSV(file, deckName || undefined, language, cardType);
      if (response.success && response.deck) {
        navigate(`/decks/${response.deck.id}/edit`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import CSV');
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    multiple: false,
    disabled: loading,
  });

  const handleTextImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textData.trim() || !deckName.trim()) {
      setError('Please provide both deck name and text data');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await importApi.fromText(textData, deckName, language, separator, cardType);
      if (response.success && response.deck) {
        navigate(`/decks/${response.deck.id}/edit`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import text');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <button
        onClick={() => navigate('/')}
        className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-6"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>Back to Dashboard</span>
      </button>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Import Cards
        </h2>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        <div className="flex space-x-4 mb-8">
          <button
            onClick={() => setImportType('csv')}
            className={`flex-1 py-3 rounded-lg font-medium transition ${
              importType === 'csv'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Import from CSV
          </button>
          <button
            onClick={() => setImportType('text')}
            className={`flex-1 py-3 rounded-lg font-medium transition ${
              importType === 'text'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Import from Text
          </button>
        </div>

        {importType === 'csv' ? (
          <div>
            <div className="mb-6 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Deck Name (Optional)
                </label>
                <input
                  type="text"
                  value={deckName}
                  onChange={(e) => setDeckName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Leave empty to use filename"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="spanish">Spanish</option>
                  <option value="english">English</option>
                  <option value="french">French</option>
                  <option value="german">German</option>
                  <option value="italian">Italian</option>
                  <option value="portuguese">Portuguese</option>
                  <option value="russian">Russian</option>
                  <option value="japanese">Japanese</option>
                  <option value="chinese">Chinese</option>
                  <option value="korean">Korean</option>
                  <option value="generic">Other</option>
                </select>
              </div>
            </div>

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition ${
                isDragActive
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
              } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <input {...getInputProps()} />
              <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              {loading ? (
                <p className="text-lg text-gray-600 dark:text-gray-400">Importing...</p>
              ) : isDragActive ? (
                <p className="text-lg text-primary-600 dark:text-primary-400">Drop the CSV file here</p>
              ) : (
                <>
                  <p className="text-lg text-gray-700 dark:text-gray-300 mb-2">
                    Drag & drop a CSV file here, or click to browse
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    CSV files with Front/Back columns for basic cards,
                    <br />
                    or Text/Translation/Explanation for cloze cards
                  </p>
                </>
              )}
            </div>
          </div>
        ) : (
          <form onSubmit={handleTextImport} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Deck Name *
                </label>
                <input
                  type="text"
                  required
                  value={deckName}
                  onChange={(e) => setDeckName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="spanish">Spanish</option>
                  <option value="english">English</option>
                  <option value="french">French</option>
                  <option value="german">German</option>
                  <option value="italian">Italian</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Separator
                </label>
                <select
                  value={separator}
                  onChange={(e) => setSeparator(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="\t">Tab</option>
                  <option value=",">Comma</option>
                  <option value=";">Semicolon</option>
                  <option value="|">Pipe</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Card Type
                </label>
                <select
                  value={cardType}
                  onChange={(e) => setCardType(e.target.value as any)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="basic">Basic</option>
                  <option value="cloze">Cloze</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Text Data *
              </label>
              <textarea
                required
                value={textData}
                onChange={(e) => setTextData(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white font-mono text-sm"
                rows={12}
                placeholder={`Enter one card per line, separated by ${separator === '\t' ? 'tabs' : separator}:\n\nExample:\nHello${separator === '\t' ? '\t' : separator}Hola\nGoodbye${separator === '\t' ? '\t' : separator}Adiós\nThank you${separator === '\t' ? '\t' : separator}Gracias`}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <FileText className="w-5 h-5" />
              <span>{loading ? 'Importing...' : 'Import Text'}</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
