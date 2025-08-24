# GraphApp Backend

A backend service for managing entities, relationships, and graph data using FastAPI and PostgreSQL.

## Features

- CRUD operations for entities and relationships
- Graph retrieval with filtering and neighborhood traversal
- Async database operations with SQLAlchemy and asyncpg
- Database migrations with Alembic
- Structured JSON logging
- Environment-based configuration
- Health check endpoints

## Setup and Running

### Prerequisites

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) package manager

### Environment Variables

Copy the example environment file and adjust as needed:

```bash
cp ../env.example .env
```

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

## REST API Testing

The `rest/` directory contains HTTP files for testing the API endpoints:

- `entity.http`: Tests for entity CRUD operations
- `relationships.http`: Tests for relationship CRUD operations
- `graph.http`: Tests for graph retrieval endpoints
- `test_graph_api.sh`: Shell script with curl commands for testing graph endpoints

You can run the HTTP files directly in VS Code with the REST Client extension, or execute the shell script to test the graph API endpoints with curl.

## Project Structure

```
backend/
├── app/                    # Main application package
│   ├── api/                # API endpoints
│   ├── db/                 # Database configuration
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── config.py           # Application configuration
│   ├── logging.py          # Logging configuration
│   └── main.py             # FastAPI application
├── migrations/             # Alembic migrations
├── rest/                   # REST API testing files
│   ├── entity.http         # Entity API tests
│   ├── relationships.http  # Relationship API tests
│   ├── graph.http          # Graph API tests
│   └── test_graph_api.sh   # Graph API test script
├── tests/                  # Test suite
├── pyproject.toml          # Project dependencies and metadata
└── alembic.ini             # Alembic configuration
```
