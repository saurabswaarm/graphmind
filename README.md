# GraphApp Monorepo

A full-stack application with a FastAPI backend for managing entities, relationships, and graph data, and a React TypeScript frontend for visualization.

## Architecture

This monorepo contains:
- **Backend**: FastAPI service with PostgreSQL for graph data management
- **Frontend**: React TypeScript application with Vite for graph visualization

## Quick Start

### Prerequisites

- **Backend**: Python 3.12+, [UV](https://github.com/astral-sh/uv) package manager
- **Frontend**: Node.js 18+, npm

### Setup

1. **Install frontend dependencies**:
```bash
npm run install:frontend
```

2. **Setup backend environment**:
```bash
npm run setup:backend
```

3. **Configure environment variables**:
```bash
cp env.example .env
```

4. **Run database migrations**:
```bash
npm run migrate:backend
```

### Development

Start both services in development mode:

```bash
# Backend (FastAPI) - http://localhost:8000
npm run dev:backend

# Frontend (React) - http://localhost:5173
npm run dev:frontend
```

## API Documentation

When the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
graphapp/
├── backend/                # FastAPI backend
│   ├── app/                # Main application package
│   │   ├── api/            # API endpoints
│   │   ├── db/             # Database configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # FastAPI application
│   ├── migrations/         # Alembic migrations
│   ├── rest/               # REST API testing files
│   └── pyproject.toml      # Backend dependencies
├── frontend/               # React TypeScript frontend
│   ├── src/                # Source code
│   ├── public/             # Static assets
│   ├── package.json        # Frontend dependencies
│   └── vite.config.ts      # Vite configuration
├── package.json            # Monorepo scripts
└── README.md               # This file
```

## Available Scripts

- `npm run dev:frontend` - Start frontend development server
- `npm run dev:backend` - Start backend development server
- `npm run build:frontend` - Build frontend for production
- `npm run install:frontend` - Install frontend dependencies
- `npm run setup:backend` - Setup backend virtual environment
- `npm run migrate:backend` - Run database migrations
- `npm run clean` - Clean build artifacts and dependencies

## Features

### Backend
- CRUD operations for entities and relationships
- Graph retrieval with filtering and neighborhood traversal
- Async database operations with SQLAlchemy and asyncpg
- Database migrations with Alembic
- Structured JSON logging
- Environment-based configuration
- Health check endpoints

### Frontend
- React 19 with TypeScript
- Vite for fast development and building
- Modern ES modules
- Hot module replacement (HMR)
- ESLint for code quality
