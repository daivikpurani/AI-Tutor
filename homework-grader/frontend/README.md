# Frontend — React + TypeScript (Webpack)

Minimal demo UI for the AI Homework Grading System. Built with **React 18** and **TypeScript**, bundled with **Webpack** (no Vite).

## Prerequisites

- Node.js 18+
- Backend running at `http://localhost:8000` (for API calls)

## Setup

```bash
cd frontend
npm install
```

## Development

```bash
npm start
```

- App: http://localhost:3000  
- API requests to `/api` and `/health` are proxied to the backend (see `webpack.config.js`).

## Build

```bash
npm run build
```

Output is in `frontend/dist/`. Serve with any static file server.

## Demo workflow

1. **Upload Materials** — Professor: pick a section, enter title, upload a PDF. File is chunked and indexed in the section’s vector store for RAG.
2. **Upload Submission** — Student: pick an assignment and student (must be enrolled), upload a homework PDF.
3. **Grade** — Pick an assignment, load submissions, then click “Grade with AI” on a submission. The backend runs RAG (section materials) + rubric + Gemini and returns score, summary, strengths, weaknesses, suggestions.
4. **View Materials** — List materials for a section by ID (seeded sections: 1–8).
