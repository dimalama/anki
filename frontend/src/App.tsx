import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import DeckCreate from './pages/DeckCreate';
import DeckEdit from './pages/DeckEdit';
import Import from './pages/Import';
import './index.css';

function App() {
  return (
    <BrowserRouter basename="/anki">
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="decks/create" element={<DeckCreate />} />
          <Route path="decks/:deckId/edit" element={<DeckEdit />} />
          <Route path="import" element={<Import />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
