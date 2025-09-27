# Development Setup Guide

This guide provides step-by-step instructions for setting up the RAG Web Application development environment.

## Quick Start

### 1. Prerequisites Check
```bash
# Check Python version (3.10+ required)
python --version

# Check Node.js version (18+ required)
node --version

# Check npm version
npm --version
```

### 2. Environment Setup

#### Backend Environment
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys and database credentials
```

#### Frontend Environment
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Optional: Install globally for convenience
npm install -g typescript vite
```

### 3. Database Setup

#### Supabase Setup
1. Create a new Supabase project
2. Enable the `pgvector` extension in SQL editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Copy your project URL and API keys to `.env`

#### Local PostgreSQL (Alternative)
```bash
# Install PostgreSQL with pgvector
brew install postgresql pgvector  # macOS
# OR
sudo apt-get install postgresql-14 postgresql-14-pgvector  # Ubuntu

# Create database
createdb rag_database

# Update DATABASE_URL in .env
```

### 4. Development Servers

#### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

### 5. Verification

1. Backend health check: `curl http://localhost:8000/health`
2. Frontend: Open `http://localhost:5173` in browser
3. API docs: Visit `http://localhost:8000/docs`

## Environment Variables

### Backend (.env)
```env
# Required
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_api_key

# Optional
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

## Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest -v
pytest --cov=app tests/  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm run lint
npm run type-check
npm run build
```

## Common Development Tasks

### Adding New Dependencies

#### Backend
```bash
cd backend
source venv/bin/activate
pip install package_name
pip freeze > requirements.txt
```

#### Frontend
```bash
cd frontend
npm install package_name
# For dev dependencies
npm install -D package_name
```

### Database Migrations
```bash
# If using Alembic for migrations
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Code Formatting
```bash
# Backend
cd backend
black .
flake8 .

# Frontend
cd frontend
npm run lint
npm run lint -- --fix
```

## Troubleshooting

### Port Conflicts
```bash
# Find process using port
lsof -ti:8000
lsof -ti:5173

# Kill process
kill -9 PID
```

### Python Environment Issues
```bash
# Reset virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Module Issues
```bash
# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Database Connection Issues
```bash
# Test database connection
python -c "
from app.db.supabase_client import get_supabase_client
client = get_supabase_client()
print('Connection successful!')
"
```

## IDE Setup

### VS Code Extensions
- Python
- TypeScript and JavaScript Language Features
- Tailwind CSS IntelliSense
- ESLint
- Prettier

### PyCharm/IntelliJ
- Configure Python interpreter to use virtual environment
- Enable TypeScript support
- Install Tailwind CSS plugin

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Descriptive commit message"

# Push branch
git push origin feature/your-feature-name

# Create pull request on GitHub
```