# Graph Service API

A backend service for managing entities, relationships, and graph data using FastAPI and PostgreSQL.

## Features

- CRUD operations for entities and relationships
- Graph retrieval with filtering and neighborhood traversal
- Async database operations with SQLAlchemy and asyncpg
- Database migrations with Alembic
- Structured JSON logging
- Environment-based configuration
- Containerized with Docker and docker-compose
- Health check endpoints

## Setup and Running

### Prerequisites

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) package manager
- Docker and docker-compose

### Environment Variables

Copy the example environment file and adjust as needed:

```bash
cp env.example .env
```

### Running with Docker

```bash
docker-compose up
```

The API will be available at http://localhost:8000

### Development Setup

1. Create a virtual environment and install dependencies:

```bash
uv venv
uv pip install -e .
```

2. Run the database migrations:

```bash
uv run alembic upgrade head
```

3. Run the API server:

```bash
uv run uvicorn app.main:app --reload
```

## API Documentation

When running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with:

```bash
uv run pytest
```

## Project Structure

```
graphapp/
├── app/                    # Main application package
│   ├── api/                # API endpoints
│   ├── db/                 # Database configuration
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── config.py           # Application configuration
│   ├── logging.py          # Logging configuration
│   └── main.py             # FastAPI application
├── migrations/             # Alembic migrations
├── tests/                  # Test suite
├── Dockerfile              # Docker build instructions
├── docker-compose.yml      # Docker services configuration
├── pyproject.toml          # Project dependencies and metadata
└── env.example             # Example environment variables
```
