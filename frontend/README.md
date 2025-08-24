# GraphApp Frontend

React TypeScript frontend for the GraphApp monorepo.

## Development

From the monorepo root:

```bash
# Install dependencies
npm run install:frontend

# Start development server
npm run dev:frontend
```

Or from this directory:

```bash
# Install dependencies
npm install

# Start development server  
npm run dev
```

## Features

- React 19 with TypeScript
- Vite for fast development and building
- ESLint for code quality
- Hot Module Replacement (HMR)

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

## Project Structure

```
src/
├── App.tsx          # Main App component
├── App.css          # App styles
├── main.tsx         # Application entry point
└── vite-env.d.ts    # Vite type definitions
```
