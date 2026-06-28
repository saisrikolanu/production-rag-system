"""
PostgreSQL database handler
Manages query logging, metrics storage, and history retrieval
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from config import Config

logger = logging.getLogger(__name__)

Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class QueryLog(Base):
    """Query log table"""
    __tablename__ = "query_logs"
    
    id = Column(String, primary_key=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)
    faithfulness = Column(Float, default=0.0)
    answer_relevance = Column(Float, default=0.0)
    context_relevance = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentLog(Base):
    """Document ingestion log table"""
    __tablename__ = "document_logs"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # 'file' or 'url'
    chunk_count = Column(Integer, default=0)
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemMetrics(Base):
    """System metrics table"""
    __tablename__ = "system_metrics"
    
    id = Column(String, primary_key=True)
    total_queries = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    avg_latency = Column(Float, default=0.0)
    avg_faithfulness = Column(Float, default=0.0)
    avg_relevance = Column(Float, default=0.0)
    total_documents = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# DATABASE HANDLER
# ============================================================================

class PostgresDB:
    """Handle PostgreSQL operations"""
    
    def __init__(self, config: Config):
        self.config = config
        self.connection_string = (
            f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@"
            f"{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
        )
        self.engine = None
        self.SessionLocal = None
    
    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            logger.info("📦 Initializing PostgreSQL database...")
            
            # Create engine with connection pooling
            self.engine = create_engine(
                self.connection_string,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("✓ PostgreSQL database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing database: {str(e)}")
            raise
    
    async def log_query(
        self,
        query: str,
        answer: str,
        sources: List[str],
        metrics: Dict[str, float],
        latency_ms: float,
        query_id: Optional[str] = None
    ) -> str:
        """Log a query and its results"""
        try:
            import uuid
            
            if not query_id:
                query_id = str(uuid.uuid4())
            
            session = self.SessionLocal()
            
            log_entry = QueryLog(
                id=query_id,
                query=query,
                answer=answer,
                sources=sources,
                faithfulness=metrics.get("faithfulness", 0.0),
                answer_relevance=metrics.get("answer_relevance", 0.0),
                context_relevance=metrics.get("context_relevance", 0.0),
                latency_ms=latency_ms
            )
            
            session.add(log_entry)
            session.commit()
            
            logger.info(f"✓ Logged query: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"❌ Error logging query: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()
    
    async def log_document(
        self,
        doc_id: str,
        filename: str,
        chunk_count: int,
        source_type: str = "file",
        file_size: int = 0
    ):
        """Log document ingestion"""
        try:
            session = self.SessionLocal()
            
            log_entry = DocumentLog(
                id=doc_id,
                filename=filename,
                source_type=source_type,
                chunk_count=chunk_count,
                file_size=file_size
            )
            
            session.add(log_entry)
            session.commit()
            
            logger.info(f"✓ Logged document: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error logging document: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()
    
    async def get_query_history(
        self,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Get query history with pagination"""
        try:
            session = self.SessionLocal()
            
            queries = session.query(QueryLog)\
                .order_by(QueryLog.created_at.desc())\
                .limit(limit)\
                .offset(skip)\
                .all()
            
            history = [
                {
                    "id": q.id,
                    "query": q.query,
                    "answer": q.answer[:100] + "..." if len(q.answer) > 100 else q.answer,
                    "faithfulness": q.faithfulness,
                    "answer_relevance": q.answer_relevance,
                    "latency_ms": q.latency_ms,
                    "created_at": q.created_at.isoformat()
                }
                for q in queries
            ]
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Error retrieving history: {str(e)}")
            return []
        finally:
            session.close()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        try:
            session = self.SessionLocal()
            
            # Query logs
            query_count = session.query(QueryLog).count()
            
            if query_count == 0:
                return {
                    "avg_latency": 0,
                    "avg_faithfulness": 0,
                    "avg_relevance": 0
                }
            
            from sqlalchemy import func
            
            avg_latency = session.query(func.avg(QueryLog.latency_ms)).scalar() or 0
            avg_faithfulness = session.query(func.avg(QueryLog.faithfulness)).scalar() or 0
            avg_relevance = session.query(func.avg(QueryLog.answer_relevance)).scalar() or 0
            
            doc_count = session.query(DocumentLog).count()
            
            return {
                "total_queries": query_count,
                "avg_latency": float(avg_latency),
                "avg_faithfulness": float(avg_faithfulness),
                "avg_relevance": float(avg_relevance),
                "total_documents": doc_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting metrics: {str(e)}")
            return {}
        finally:
            session.close()
    
    async def close(self):
        """Close database connection"""
        try:
            if self.engine:
                self.engine.dispose()
            logger.info("✓ Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}")