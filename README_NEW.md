# 🎴 Anki Deck Generator - Full Stack Edition

A modern, full-stack web application for creating and managing Anki flashcard decks. Built with FastAPI backend and React frontend.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-38B2AC?style=flat&logo=tailwind-css&logoColor=white)

## ✨ Features

### 🎯 Core Features
- **Create Decks** - Interactive deck builder with multiple card types
- **Edit Cards** - Spreadsheet-like interface for bulk editing
- **Import** - CSV upload or text paste with auto-detection
- **Download** - Generate and download .apkg files ready for Anki
- **Smart Tagging** - Automatic tag generation based on content
- **Multi-language** - Support for 10+ languages
- **Template System** - Customizable card templates

### 🎨 Modern UI
- Clean, responsive design
- Dark mode support
- Drag & drop file uploads
- Real-time validation
- Intuitive navigation

### 🚀 Tech Highlights
- **REST API** - Well-documented FastAPI backend
- **Type Safety** - Full TypeScript support
- **Fast** - Vite build tool, optimized performance
- **Scalable** - Modular architecture

## 📁 Project Structure

```
anki/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/endpoints/     # REST API routes
│   │   ├── models/            # Pydantic models
│   │   ├── services/          # Business logic
│   │   └── main.py            # FastAPI app
│   └── requirements.txt
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── pages/             # Page views
│   │   ├── services/          # API client
│   │   └── types/             # TypeScript types
│   └── package.json
│
├── anki_deck_generator/        # Core Python library
│   ├── core.py                # Deck generation logic
│   ├── config.py              # Configuration
│   └── auto_generator.py      # Batch operations
│
├── csv/                        # Input CSV files
├── apkg/                       # Generated Anki decks
└── config/                     # Configuration files
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

3. Start backend server:
```bash
cd backend
python -m app.main
```

Backend API will be available at http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env if needed (default backend URL: http://localhost:8000/api/v1)
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at http://localhost:5173

## 🎮 Usage

### Creating a Deck

1. Click "New Deck" button
2. Fill in deck details:
   - Name
   - Language
   - Card type (Basic, Cloze, or Reversed)
   - Tags
3. Click "Create Deck"
4. Add cards in the editor
5. Save and download

### Importing Cards

#### From CSV:
1. Go to Import page
2. Drag & drop or click to upload CSV file
3. CSV format:
   ```csv
   Front,Back
   Hello,Hola
   Goodbye,Adiós
   ```

#### From Text:
1. Go to Import page → "Import from Text"
2. Paste tab or comma-separated data
3. Set separator and deck name
4. Click "Import"

### Downloading Decks

1. On Dashboard, find your deck
2. Click "Download" button
3. Import the `.apkg` file into Anki

## 📚 API Documentation

### Endpoints

**Decks**
- `GET /api/v1/decks` - List all decks
- `POST /api/v1/decks` - Create deck
- `GET /api/v1/decks/{id}` - Get deck
- `PUT /api/v1/decks/{id}` - Update deck
- `DELETE /api/v1/decks/{id}` - Delete deck
- `POST /api/v1/decks/{id}/generate` - Generate .apkg
- `GET /api/v1/decks/{id}/download` - Download .apkg

**Cards**
- `GET /api/v1/cards/{deck_id}/cards` - List cards
- `POST /api/v1/cards/{deck_id}/cards` - Create card
- `POST /api/v1/cards/{deck_id}/cards/batch` - Bulk create
- `PUT /api/v1/cards/{deck_id}/cards/{id}` - Update card
- `DELETE /api/v1/cards/{deck_id}/cards/{id}` - Delete card

**Import**
- `POST /api/v1/import/csv` - Import CSV
- `POST /api/v1/import/text` - Import text

**Templates & Tags**
- `GET /api/v1/templates` - List templates
- `GET /api/v1/tags` - Get tags

Full API documentation available at http://localhost:8000/api/docs when server is running.

## 🛠️ Development

### Backend Development

```bash
cd backend
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev  # Start with hot reload
npm run build  # Build for production
npm run preview  # Preview production build
```

### Code Structure

**Backend**
- `api/endpoints/` - Route handlers
- `models/` - Pydantic models for validation
- `services/` - Business logic layer
- `core/` - Configuration and settings

**Frontend**
- `components/` - Reusable UI components
- `pages/` - Page-level components
- `services/api.ts` - API client
- `types/` - TypeScript type definitions

## 🎨 Customization

### Card Templates

Create custom templates in `config/config.json`:

```json
{
  "templates": {
    "basic": {
      "name": "My Template",
      "qfmt": "{{Front}}",
      "afmt": "{{FrontSide}}<hr>{{Back}}"
    }
  },
  "css": ".card { font-family: Arial; font-size: 20px; }"
}
```

### Tags

Configure custom tag patterns:

```json
{
  "custom_tags": {
    "*_verb_*.csv": ["verb", "grammar"],
    "*_vocab_*.csv": ["vocabulary"]
  }
}
```

## 📦 Deployment

### Backend Deployment

Deploy to any Python-compatible platform:
- Heroku
- AWS (Elastic Beanstalk, Lambda)
- Google Cloud Run
- DigitalOcean App Platform

### Frontend Deployment

Deploy to static hosting:
- Vercel (recommended)
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

Remember to set `VITE_API_URL` environment variable to your backend URL.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 🆕 What's New in This Version

### Major Updates
- ✅ Full-stack web application with REST API
- ✅ Modern React frontend with TypeScript
- ✅ Interactive deck and card editing
- ✅ Drag & drop file uploads
- ✅ Real-time preview and validation
- ✅ Dark mode support
- ✅ Comprehensive API documentation
- ✅ Better error handling and user feedback

### Legacy CLI Still Available
The original CLI tool (`auto_generate_decks.py`) is still available and fully functional for those who prefer command-line workflows.

## 📞 Support

For issues and questions:
- GitHub Issues: [Report a bug](https://github.com/dimalama/anki/issues)
- Documentation: Check README files in `/backend` and `/frontend`

---

Made with ❤️ for language learners
