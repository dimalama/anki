# Anki Deck Generator - Frontend

Modern React + TypeScript frontend for the Anki Deck Generator application.

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Zustand** - State management
- **Lucide React** - Icons
- **React Dropzone** - File uploads

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env to set your backend API URL (default: http://localhost:8000/api/v1)
```

3. Run development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Features

### Dashboard
- View all decks
- Quick actions: download, edit, delete
- Filter by language and tags
- Card count and metadata display

### Deck Creation
- Create new decks with customizable settings
- Choose card type: basic, cloze, or reversed
- Set language and tags
- Simple, guided workflow

### Deck Editing
- Spreadsheet-like card editor
- Add/edit cards inline
- Bulk operations
- Real-time updates

### Import
- **CSV Import**: Drag & drop CSV files
- **Text Import**: Paste tab/comma-separated data
- Auto-detect card structure
- Customizable separators

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable components
│   │   └── layout/     # Layout components
│   ├── pages/          # Page components
│   │   ├── Dashboard.tsx
│   │   ├── DeckCreate.tsx
│   │   ├── DeckEdit.tsx
│   │   └── Import.tsx
│   ├── services/       # API client
│   │   └── api.ts
│   ├── types/          # TypeScript types
│   │   └── index.ts
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Entry point
├── public/             # Static assets
└── package.json
```

## API Integration

The frontend communicates with the FastAPI backend through the API client (`src/services/api.ts`).

Key API modules:
- `decksApi` - Deck CRUD operations
- `cardsApi` - Card management
- `templatesApi` - Template management
- `importApi` - Import operations

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:8000/api/v1)

## Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

## Deployment

The frontend can be deployed to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- etc.

Make sure to set the `VITE_API_URL` environment variable to your production backend URL.
