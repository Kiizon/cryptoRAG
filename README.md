# CryptoRAG

RAG-powered AI chatbot for cryptography education.

>This project was inspired by the course [CPS 633](https://www.torontomu.ca/calendar/2025-2026/courses/computer-science/CPS/633/).

**Note:** Recently migrated from a Streamlit app to a React + FastAPI app.

## Uses:
- **Frontend:** Next.js, Tailwind CSS, Framer Motion
- **Backend:** FastAPI, Python
- **AI/RAG:** Cohere (Command R+, Embed v3, Rerank v3), Unstructured, PDFMiner

## Usage

### Backend
Maneuver to the `api` directory and start the server:
```bash
uvicorn api.index:app --reload
```

### Frontend
Maneuver to the `frontend` directory and start the client:
```bash
npm run dev
```

The app will ingest sources (including *Crypto 101*) on startup and be ready for queries.