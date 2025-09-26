# RAG Document Intelligence Frontend

A modern React frontend for the RAG (Retrieval-Augmented Generation) Document Intelligence system.

## Features

- **Two-Panel Interface**: Upload documents on the left, search and summarize on the right
- **Document Upload**: Drag-and-drop ZIP files containing PDF, DOCX, or TXT documents
- **Intelligent Search**: Search across entire documents or specific pages with AI-powered semantic search
- **Document Summarization**: Generate AI summaries of individual pages
- **Interactive Results**: View search results with highlighted matches and navigate to specific pages
- **Responsive Design**: Modern, clean interface built with Tailwind CSS

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Axios** for API communication
- **Headless UI** for accessible components

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on `http://127.0.0.1:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

## Usage

1. **Upload Documents**: Drag and drop a ZIP file containing your documents (PDF, DOCX, TXT) into the left panel
2. **Navigate Pages**: Once uploaded, browse through the document pages using the navigation controls
3. **Search**: Enter queries in the right panel to find relevant content across your documents
4. **Summarize**: Select a page and generate an AI summary of its content
5. **View Results**: Search results show relevant snippets with highlighted matches

## API Integration

The frontend communicates with the FastAPI backend through these endpoints:

- `POST /upload-zip` - Upload document archives
- `POST /search` - Semantic search across documents
- `GET /summarize-page/{chunk_id}` - Generate page summaries
- `GET /healthz` - Health check

## Configuration

Update the API base URL in `src/api.ts` if your backend runs on a different address:

```typescript
const API_BASE_URL = 'http://your-backend-url:port';
```