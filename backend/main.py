"""
Production RAG System - FastAPI Backend
Main application with all API endpoints
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

from models import (
    QueryRequest,
    QueryResponse,
    DocumentUploadResponse,
    URLIngestResponse,
    HealthResponse,
    MetricsResponse
)
from rag.processor import DocumentProcessor
from rag.url_fetcher import URLFetcher
from rag.embedder import EmbeddingPipeline
from rag.retriever import RAGRetriever
from rag.evaluator import RAGEvaluator
from rag.pinecone_handler import PineconeHandler
from db.postgres import PostgresDB
from utils.logging import setup_logging, get_logger
from config import Config

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize configuration
config = Config()

# Initialize FastAPI app
app = FastAPI(
    title="Production RAG System",
    description="Production-grade Retrieval-Augmented Generation with quality evaluation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state - initialized at startup
class AppState:
    doc_processor: DocumentProcessor = None
    url_fetcher: URLFetcher = None
    embedder: EmbeddingPipeline = None
    retriever: RAGRetriever = None
    evaluator: RAGEvaluator = None
    postgres_db: PostgresDB = None
    pinecone_handler: PineconeHandler = None
    query_count: int = 0
    error_count: int = 0

app_state = AppState()

@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup"""
    try:
        logger.info("🚀 Starting up Production RAG System...")
        
        # Initialize Pinecone
        app_state.pinecone_handler = PineconeHandler(config)
        logger.info("✓ Pinecone initialized")
        
        # Initialize PostgreSQL
        app_state.postgres_db = PostgresDB(config)
        await app_state.postgres_db.initialize()
        logger.info("✓ PostgreSQL initialized")
        
        # Initialize RAG components
        app_state.doc_processor = DocumentProcessor(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        logger.info("✓ Document processor ready")
        
        app_state.url_fetcher = URLFetcher(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        logger.info("✓ URL fetcher ready")
        
        app_state.embedder = EmbeddingPipeline(config)
        logger.info("✓ Embedding pipeline ready")
        
        app_state.retriever = RAGRetriever(
            pinecone=app_state.pinecone_handler,
            embedder=app_state.embedder,
            config=config
        )
        logger.info("✓ RAG retriever ready")
        
        app_state.evaluator = RAGEvaluator(config)
        logger.info("✓ RAGAS evaluator ready")
        
        logger.info("✅ All components initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down...")
    try:
        if app_state.postgres_db:
            await app_state.postgres_db.close()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        components={
            "pinecone": "ready",
            "postgres": "ready",
            "embedder": "ready",
            "evaluator": "ready"
        }
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get system metrics and evaluation statistics"""
    try:
        metrics = await app_state.postgres_db.get_metrics()
        return MetricsResponse(
            total_queries=app_state.query_count,
            total_errors=app_state.error_count,
            error_rate=app_state.error_count / max(app_state.query_count, 1),
            avg_latency=metrics.get("avg_latency", 0),
            avg_faithfulness=metrics.get("avg_faithfulness", 0),
            avg_relevance=metrics.get("avg_relevance", 0),
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

# ============================================================================
# DOCUMENT UPLOAD ENDPOINTS
# ============================================================================

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_documents(files: list[UploadFile] = File(...)):
    """
    Upload documents for RAG indexing
    Supports: PDF, TXT, DOCX
    """
    try:
        logger.info(f"📄 Received {len(files)} documents for upload")
        
        document_ids = []
        total_chunks = 0
        
        for file in files:
            try:
                # Validate file type
                file_ext = file.filename.split('.')[-1].lower()
                if file_ext not in ['pdf', 'txt', 'docx']:
                    logger.warning(f"⚠️ Skipping unsupported file: {file.filename}")
                    continue
                
                # Read file content
                content = await file.read()
                
                # Process document
                logger.info(f"Processing: {file.filename}")
                chunks = app_state.doc_processor.process(
                    filename=file.filename,
                    content=content,
                    file_type=file_ext
                )
                
                if not chunks:
                    continue
                
                # Generate embeddings
                embeddings = await app_state.embedder.embed_texts(
                    [chunk["text"] for chunk in chunks]
                )
                
                # Store in Pinecone
                doc_id = await app_state.pinecone_handler.upsert_vectors(
                    chunks=chunks,
                    embeddings=embeddings,
                    metadata={
                        "filename": file.filename,
                        "upload_time": datetime.utcnow().isoformat()
                    }
                )
                
                document_ids.append(doc_id)
                total_chunks += len(chunks)
                
                # Log to database
                await app_state.postgres_db.log_document(
                    doc_id=doc_id,
                    filename=file.filename,
                    chunk_count=len(chunks),
                    source_type="file",
                    file_size=len(content)
                )
                
                logger.info(f"✓ Indexed {file.filename} ({len(chunks)} chunks)")
                
            except Exception as e:
                logger.error(f"❌ Error processing {file.filename}: {str(e)}")
                app_state.error_count += 1
                continue
        
        if not document_ids:
            raise HTTPException(status_code=400, detail="No valid documents to process")
        
        return DocumentUploadResponse(
            success=True,
            document_ids=document_ids,
            chunks_created=total_chunks,
            message=f"Successfully indexed {len(document_ids)} documents ({total_chunks} chunks)"
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        app_state.error_count += 1
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# URL INGESTION ENDPOINTS
# ============================================================================

@app.post("/documents/ingest-url", response_model=URLIngestResponse)
async def ingest_url(url: str = Query(...), name: str = Query(None)):
    """
    Ingest content from URL
    Supports: Any website with text content
    """
    try:
        logger.info(f"🌐 Ingesting URL: {url}")
        
        # Fetch and process URL
        chunks = await app_state.url_fetcher.fetch_and_process(url, name)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No content extracted from URL"
            )
        
        # Generate embeddings
        embeddings = await app_state.embedder.embed_texts(
            [chunk["text"] for chunk in chunks]
        )
        
        # Store in Pinecone
        doc_id = await app_state.pinecone_handler.upsert_vectors(
            chunks=chunks,
            embeddings=embeddings,
            metadata={
                "source_url": url,
                "ingestion_time": datetime.utcnow().isoformat()
            }
        )
        
        # Log to database
        await app_state.postgres_db.log_document(
            doc_id=doc_id,
            filename=name or url,
            chunk_count=len(chunks),
            source_type="url"
        )
        
        logger.info(f"✓ Ingested URL {url} ({len(chunks)} chunks)")
        
        return URLIngestResponse(
            success=True,
            source=url,
            chunks_created=len(chunks),
            message=f"Successfully ingested URL ({len(chunks)} chunks)"
        )
        
    except Exception as e:
        logger.error(f"❌ URL ingestion failed: {str(e)}", exc_info=True)
        app_state.error_count += 1
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# QUERY ENDPOINTS
# ============================================================================

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system
    Returns: Answer + source documents + quality metrics
    """
    start_time = datetime.utcnow()
    app_state.query_count += 1
    query_id = str(uuid.uuid4())
    
    try:
        logger.info(f"🔍 Query ({query_id}): {request.query}")
        
        # Retrieve relevant documents
        retrieved_docs = await app_state.retriever.retrieve(
            query=request.query,
            top_k=request.top_k
        )
        
        if not retrieved_docs:
            logger.warning("No relevant documents found")
            return QueryResponse(
                query=request.query,
                answer="No relevant documents found.",
                sources=[],
                metrics={
                    "faithfulness": 0,
                    "answer_relevance": 0,
                    "latency_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
                }
            )
        
        # Generate answer using LLM
        answer = await app_state.retriever.generate_answer(
            query=request.query,
            context_docs=retrieved_docs
        )
        
        # Evaluate quality using RAGAS
        evaluation_scores = await app_state.evaluator.evaluate(
            query=request.query,
            answer=answer,
            context=[doc["text"] for doc in retrieved_docs]
        )
        
        # Calculate latency
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Log to database
        await app_state.postgres_db.log_query(
            query=request.query,
            answer=answer,
            sources=[doc["filename"] for doc in retrieved_docs],
            metrics=evaluation_scores,
            latency_ms=latency_ms,
            query_id=query_id
        )
        
        logger.info(
            f"✓ Query answered in {latency_ms:.2f}ms "
            f"(Faithfulness: {evaluation_scores['faithfulness']:.2f}, "
            f"Relevance: {evaluation_scores['answer_relevance']:.2f})"
        )
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=[
                {
                    "filename": doc["filename"],
                    "text": doc["text"][:300],
                    "relevance_score": doc.get("score", 0)
                }
                for doc in retrieved_docs
            ],
            metrics={
                "faithfulness": evaluation_scores["faithfulness"],
                "answer_relevance": evaluation_scores["answer_relevance"],
                "context_relevance": evaluation_scores.get("context_relevance", 0),
                "latency_ms": latency_ms
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Query failed: {str(e)}", exc_info=True)
        app_state.error_count += 1
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# ============================================================================
# HISTORY ENDPOINTS
# ============================================================================

@app.get("/history")
async def get_query_history(limit: int = Query(50, ge=1, le=100), skip: int = Query(0, ge=0)):
    """Get query history with pagination"""
    try:
        history = await app_state.postgres_db.get_query_history(
            limit=limit,
            skip=skip
        )
        return {"success": True, "items": history, "total": len(history)}
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Production RAG System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "upload_documents": "/documents/upload",
            "ingest_url": "/documents/ingest-url",
            "query": "/query",
            "history": "/history",
            "api_docs": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )