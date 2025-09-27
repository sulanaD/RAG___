# RAG Web Application

A full-stack Retrieval-Augmented Generation (RAG) system with a modern React frontend and FastAPI backend. This application allows users to upload documents (PDF, DOCX, TXT), organize them by folders, search through document content using AI-powered semantic search, and generate summaries.

## 🚀 Features

- **Document Upload & Management**: Upload ZIP files containing documents with folder structure preservation
- **AI-Powered Search**: Semantic search across documents using OpenAI embeddings
- **Document Summarization**: Generate intelligent summaries of document content
- **Folder Organization**: Browse documents by their original folder structure
- **Split-View Interface**: Persistent folder browser with document content display
- **Multi-Format Support**: PDF, DOCX, and TXT file processing
- **Real-time Updates**: Live search results and document navigation

## 🏗️ Architecture

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.10+
- **Database**: Supabase (PostgreSQL with vector extensions)
- **AI Services**: OpenAI GPT-4 and text-embedding-ada-002
- **Document Processing**: PyPDF, python-docx for file parsing

## 📋 Prerequisites

- **Python 3.10 or higher**
- **Node.js 18 or higher**
- **npm or yarn**
- **Supabase account** with a configured project
- **OpenAI API key**

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sulanaD/RAG_web.git
cd RAG_web
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the `backend` directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Optional: Database URL (if using direct PostgreSQL connection)
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

#### Database Setup
The application will automatically create the required tables on first run. Ensure your Supabase project has:
- Vector extension enabled (`pgvector`)
- Proper RLS policies configured

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

## 🚀 Running the Application

### 1. Start the Backend Server

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at: `http://localhost:8000`

### 2. Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at: `http://localhost:5173` (or the next available port)

### 3. Access the Application

Open your browser and navigate to the frontend URL. The application should display with:
- Upload panel for ZIP files
- Folder browser for document organization
- Search and summarization functionality

## 📚 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Key Endpoints:

- `POST /upload-zip` - Upload ZIP files with documents
- `GET /documents` - List all uploaded documents
- `POST /search` - Semantic search across documents
- `POST /summarize` - Generate document summaries
- `GET /health` - Health check endpoint

## 🎯 Usage Guide

### Uploading Documents

1. Prepare a ZIP file containing your documents in folders
2. Click the "Upload ZIP File" button in the interface
3. Select your ZIP file
4. Wait for processing to complete

### Browsing Documents

- Use the folder browser on the left to navigate your document structure
- Click on folders to expand/collapse them
- Click on documents to view their content
- Use navigation buttons to browse through document pages

### Searching Documents

1. Select a document from the folder browser
2. Enter your search query in the search box
3. Choose search scope (document or page level)
4. Click "Search" to get AI-powered semantic results

### Generating Summaries

1. Select a document
2. Choose summarization scope (document or page level)
3. Click "Summarize" to generate an AI summary

## 🔧 Configuration

### Backend Configuration (`backend/app/config.py`)

Key settings you can modify:
- Database connection parameters
- OpenAI model configurations
- File upload limits
- CORS settings

### Frontend Configuration

- API endpoint URLs in `frontend/src/api.ts`
- UI themes in `frontend/tailwind.config.js`
- Build settings in `frontend/vite.config.ts`

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run lint
npm run build  # Test build process
```

## 📦 Building for Production

### Backend Deployment

1. Set production environment variables
2. Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment

```bash
cd frontend
npm run build
```

The built files will be in the `dist` directory, ready for deployment to any static hosting service.

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**: Check Python version and virtual environment activation
2. **Database connection errors**: Verify Supabase credentials and network connectivity
3. **OpenAI API errors**: Confirm API key validity and quota availability
4. **Frontend build fails**: Ensure Node.js version compatibility and clean npm cache

### Debug Mode

Enable debug logging by setting environment variables:
```bash
export LOG_LEVEL=DEBUG
export OPENAI_LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the troubleshooting section above

## 🔄 Version History

- **v1.0.0**: Initial release with basic RAG functionality
- **v1.1.0**: Added folder organization and split-view interface
- **v1.2.0**: Enhanced search functionality and UI improvements