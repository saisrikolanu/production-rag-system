# Production RAG System

A production-grade Retrieval-Augmented Generation (RAG) system built with FastAPI (backend) and React/Next.js (frontend).

## Features

### Backend
- ✅ **Document Ingestion**: Upload PDF, TXT, DOCX files
- ✅ **URL Scraping**: Ingest content from any website
- ✅ **Semantic Search**: Vector similarity search using Pinecone
- ✅ **LLM Integration**: GPT-4 powered answer generation
- ✅ **Quality Evaluation**: RAGAS metrics for response quality
- ✅ **Structured Logging**: JSON-formatted production logs
- ✅ **Database**: PostgreSQL for query history and metrics
- ✅ **API Documentation**: Auto-generated with Swagger/OpenAPI

### Frontend
- 🔄 Coming Soon: React/Next.js UI
- 📊 Metrics Dashboard
- 📤 Document Upload Interface
- 🔗 URL Ingestion Form
- 💬 Query Interface with Results

## Tech Stack

### Backend
- **Framework**: FastAPI (async, production-ready)
- **LLM**: OpenAI GPT-4
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: Pinecone
- **Database**: PostgreSQL
- **Evaluation**: RAGAS
- **Logging**: Python JSON Logger
- **Deployment**: Docker + AWS

### Frontend
- **Framework**: React/Next.js (TypeScript)
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **API Client**: Axios

## Architecture


## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Pinecone account
- OpenAI API key

### Backend Setup

1. **Clone repository**
```bash
git clone https://github.com/saisrikolanu/production-rag-system.git
cd production-rag-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

5. **Run backend**
```bash
cd backend
uvicorn main:app --reload
```

Backend available at: http://localhost:8000

### Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:3000

## API Endpoints

### Core Endpoints

#### Document Upload
```bash
POST /documents/upload
Content-Type: multipart/form-data

# Upload PDF, TXT, or DOCX files
curl -X POST "http://localhost:8000/documents/upload" \
  -F "files=@document.pdf"
```

#### URL Ingestion
```bash
POST /documents/ingest-url?url=https://example.com&name=Example

curl -X POST "http://localhost:8000/documents/ingest-url?url=https://example.com&name=Example"
```

#### Query
```bash
POST /query
Content-Type: application/json

{
  "query": "What are the main findings?",
  "top_k": 5,
  "use_reranker": true
}

Response:
{
  "query": "What are the main findings?",
  "answer": "The study found...",
  "sources": [
    {
      "filename": "paper.pdf",
      "text": "Relevant excerpt...",
      "relevance_score": 0.95
    }
  ],
  "metrics": {
    "faithfulness": 0.94,
    "answer_relevance": 0.91,
    "context_relevance": 0.89,
    "latency_ms": 523.4
  }
}
```

#### Query History
```bash
GET /history?limit=50&skip=0

Response:
{
  "success": true,
  "items": [...],
  "total": 50
}
```

#### Metrics
```bash
GET /metrics

Response:
{
  "total_queries": 1245,
  "total_errors": 10,
  "error_rate": 0.008,
  "avg_latency": 487.3,
  "avg_faithfulness": 0.92,
  "avg_relevance": 0.89
}
```

#### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2026-06-27T...",
  "components": {
    "pinecone": "ready",
    "postgres": "ready",
    "embedder": "ready",
    "evaluator": "ready"
  }
}
```

## Environment Variables

See `backend/.env.example` for all configuration options:

- `OPENAI_API_KEY`: Your OpenAI API key
- `PINECONE_API_KEY`: Your Pinecone API key
- `POSTGRES_HOST`: PostgreSQL host
- `POSTGRES_PASSWORD`: PostgreSQL password
- `CHUNK_SIZE`: Document chunk size (default: 500)
- `TOP_K_RETRIEVAL`: Number of documents to retrieve (default: 5)

## Database Schema

### query_logs
```sql
- id (UUID)
- query (TEXT)
- answer (TEXT)
- sources (JSON)
- faithfulness (FLOAT)
- answer_relevance (FLOAT)
- context_relevance (FLOAT)
- latency_ms (FLOAT)
- created_at (TIMESTAMP)
```

### document_logs
```sql
- id (UUID)
- filename (VARCHAR)
- source_type (VARCHAR) -- 'file' or 'url'
- chunk_count (INTEGER)
- file_size (INTEGER)
- created_at (TIMESTAMP)
```

## Metrics & Evaluation

### RAGAS Scores

- **Faithfulness** (0-1): Does the answer stick to the retrieved documents?
- **Answer Relevance** (0-1): Does the answer address the query?
- **Context Relevance** (0-1): Are the retrieved documents relevant to the query?

## Deployment

### Docker

```bash
# Build image
docker build -t production-rag-system .

# Run container
docker run -p 8000:8000 --env-file .env production-rag-system
```

### AWS/Cloud

- Backend: AWS ECS + ALB
- Database: AWS RDS (PostgreSQL)
- Vector Store: Pinecone Serverless
- Storage: AWS S3 for documents

## Testing

```bash
pytest tests/
pytest tests/ -v
pytest tests/ --cov=backend
```

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Performance

- **Average Query Latency**: 400-600ms
- **Embedding Generation**: 50-100ms per 100 chunks
- **Retrieval**: <50ms (Pinecone optimized)
- **LLM Response**: 2-4s (depends on query complexity)

## Roadmap

- [ ] Frontend UI (React/Next.js)
- [ ] Advanced filtering and reranking
- [ ] Fine-tuned models
- [ ] Multi-language support
- [ ] Streaming responses
- [ ] User authentication
- [ ] Rate limiting
- [ ] Admin dashboard

## License

MIT License - see LICENSE file for details

## Author

Sai Sri Kolanu | AI Engineer
- GitHub: [@saisrikolanu](https://github.com/saisrikolanu)
- LinkedIn: [saisrikolanu](https://linkedin.com/in/saisrikolanu)
- Email: kolanusaisri13@gmail.com

## Acknowledgments

- OpenAI for GPT-4 and embeddings
- Pinecone for vector database
- LangChain for LLM orchestration
- RAGAS for evaluation framework