# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI + React.js tutorial application demonstrating Learnosity Items API integration. The application creates a web-based assessment platform using Learnosity's educational technology services with a modern frontend/backend separation.

## Architecture

This is a monorepo with separate backend and frontend applications:

- **Backend**: FastAPI with JSON API endpoints and CORS middleware
- **Frontend**: React.js (TypeScript) with Learnosity integration
- **Assessment Integration**: Learnosity SDK for educational content delivery
- **Structure**:
  - `backend/`: FastAPI Python application
    - `main.py`: FastAPI application with JSON API routes
    - `config.py`: Learnosity API credentials (demo keys)
    - `pyproject.toml`: Python dependencies
  - `frontend/`: React TypeScript application
    - `src/components/LearnosityAssessment.tsx`: Main assessment component
    - `src/App.tsx`: Main application component

## Development Commands

### Running the Backend
```bash
# Navigate to backend directory
cd backend

# Install dependencies (first time only)
uv sync

# Start FastAPI development server
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running the Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start React development server
npm start
```

### Full Development Setup

**Option 1: Manual Commands**
1. Start FastAPI backend on port 8000: `cd backend && python main.py`
2. Start React frontend on port 3000: `cd frontend && npm start`
3. Frontend will proxy API calls to backend via CORS

**Option 2: VS Code Integration**
1. Open `learnosity-fastapi.code-workspace` in VS Code
2. Use Command Palette (Ctrl/Cmd+Shift+P) to run tasks:
   - "Tasks: Run Task" → "Setup All Dependencies" (first time only)
   - "Tasks: Run Task" → "Start React Dev Server"
3. Use Debug view (F5) to launch and debug:
   - "FastAPI Backend" - Debug FastAPI with breakpoints
   - "FastAPI with Uvicorn" - Run with auto-reload
   - "Launch Full Stack" - Starts both backend and frontend together

### Dependency Management

**Backend** (Python with uv):
```bash
cd backend
# Install dependencies
uv sync

# Add new dependency
uv add package_name
```

**Frontend** (Node.js with npm):
```bash
cd frontend
npm install
npm install <package_name>
```

## Key Implementation Details

### Backend API Structure
- `/`: API information endpoint
- `/api/items`: Returns Learnosity configuration as JSON

### Frontend Architecture
- React component fetches config from FastAPI backend
- Dynamically loads Learnosity Items API script
- Renders assessment in `#learnosity_assess` div

### Learnosity Integration
- Uses `learnosity_sdk` for secure API authentication
- Security configuration includes consumer_key, user_id, and domain
- Items API requests require session_id and activity template configuration
- Assessment rendering happens client-side via Learnosity's JavaScript SDK

### CORS Configuration
- FastAPI configured to allow requests from `http://localhost:3000`
- Enables seamless frontend-backend communication during development

### Security Keys
- Demo keys are hardcoded in `config.py` for tutorial purposes
- Production deployments should use secure credential storage

## VS Code Development Features

### Workspace Configuration
- Multi-root workspace with separate folders for backend/frontend
- Python interpreter automatically configured for backend virtual environment
- TypeScript/ESLint configured for frontend development

### Debug Configurations
- **FastAPI Backend**: Debug Python code with breakpoints
- **FastAPI with Uvicorn**: Run with auto-reload for development
- **Launch Full Stack**: Combined launch that starts both services

### Available Tasks
- **Setup All Dependencies**: Install both Python and Node.js dependencies
- **Install Backend Dependencies**: Run `uv sync` in backend folder
- **Install Frontend Dependencies**: Run `npm install` in frontend folder
- **Start React Dev Server**: Launch frontend development server
- **Build Frontend**: Create production build of React app

### Recommended Extensions
- Python (ms-python.python)
- Python Debugger (ms-python.debugpy)
- TypeScript and JavaScript (ms-vscode.vscode-typescript-next)
- Prettier (esbenp.prettier-vscode)