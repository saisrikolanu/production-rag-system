"""
Pydantic models for request/response validation
Type safety and automatic validation for all API endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============================================================================
# REQUEST MODELS
# ============================================================================

class QueryRequest(BaseModel):
    """Query request to RAG system"""
    query: str = Field(..., min_length=1, max_length=1000, description="User query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of top documents to retrieve")
    use_reranker: bool = Field(default=True, description="Whether to use reranking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the main findings in the document?",
                "top_k": 5,
                "use_reranker": True
            }
        }

class DocumentUploadRequest(BaseModel):
    """Document upload request"""
    filenames: List[str] = Field(..., description="List of uploaded filenames")

class URLIngestRequest(BaseModel):
    """URL ingestion request"""
    url: str = Field(..., description="URL to ingest")
    name: Optional[str] = Field(None, description="Custom document name")

# ============================================================================
# RESPONSE MODELS
# ============================================================================

class SourceDocument(BaseModel):
    """Source document in query response"""
    filename: str
    text: str
    relevance_score: float = Field(..., ge=0, le=1)

class QueryMetrics(BaseModel):
    """Quality metrics for query response"""
    faithfulness: float = Field(..., ge=0, le=1, description="RAGAS faithfulness score")
    answer_relevance: float = Field(..., ge=0, le=1, description="RAGAS answer relevance")
    context_relevance: float = Field(default=0, ge=0, le=1, description="RAGAS context relevance")
    latency_ms: float = Field(..., ge=0, description="Query latency in milliseconds")

class QueryResponse(BaseModel):
    """Response from RAG query"""
    query: str
    answer: str
    sources: List[SourceDocument]
    metrics: QueryMetrics
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DocumentUploadResponse(BaseModel):
    """Response from document upload"""
    success: bool
    document_ids: List[str]
    chunks_created: int
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class URLIngestResponse(BaseModel):
    """Response from URL ingestion"""
    success: bool
    source: str
    chunks_created: int
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthResponse(BaseModel):
    """System health status"""
    status: str
    timestamp: str
    components: Dict[str, str]

class MetricsResponse(BaseModel):
    """System-wide metrics"""
    total_queries: int
    total_errors: int
    error_rate: float
    avg_latency: float
    avg_faithfulness: float
    avg_relevance: float
    timestamp: str

class QueryHistoryItem(BaseModel):
    """Query history item"""
    id: str
    query: str
    answer: str
    sources: List[str]
    faithfulness: float
    answer_relevance: float
    latency_ms: float
    timestamp: datetime

# ============================================================================
# INTERNAL MODELS
# ============================================================================

class ProcessedChunk(BaseModel):
    """Document chunk after processing"""
    id: str
    text: str
    filename: str
    page: Optional[int] = None
    metadata: Dict[str, Any] = {}

class RetrievedDocument(BaseModel):
    """Document retrieved from vector store"""
    id: str
    text: str
    filename: str
    score: float
    metadata: Dict[str, Any] = {}