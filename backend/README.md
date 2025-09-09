# Learnosity FastAPI Backend

FastAPI backend for the Learnosity Items API demo.

## Setup

```bash
# Install dependencies
uv sync

# Run development server
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /`: API information
- `GET /api/items`: Learnosity Items API configuration