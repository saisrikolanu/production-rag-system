"""
Pinecone vector database handler
Manages vector storage, retrieval, and search operations
"""

import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from config import Config

logger = logging.getLogger(__name__)

class PineconeHandler:
    """Handle Pinecone vector database operations"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index_name = config.PINECONE_INDEX_NAME
        self.index = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or get existing Pinecone index"""
        try:
            # Check if index exists
            indexes = self.client.list_indexes()
            index_names = [idx.name for idx in indexes]
            
            if self.index_name not in index_names:
                logger.info(f"📦 Creating Pinecone index: {self.index_name}")
                
                # Create index
                self.client.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info(f"✓ Index created: {self.index_name}")
            else:
                logger.info(f"✓ Using existing index: {self.index_name}")
            
            # Get index
            self.index = self.client.Index(self.index_name)
            
        except Exception as e:
            logger.error(f"❌ Error initializing Pinecone index: {str(e)}")
            raise
    
    async def upsert_vectors(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upsert vectors into Pinecone
        
        Args:
            chunks: List of document chunks
            embeddings: List of embedding vectors
            metadata: Additional metadata
        
        Returns:
            Document ID
        """
        try:
            logger.info(f"📤 Upserting {len(chunks)} vectors to Pinecone...")
            
            # Prepare vectors for upsert
            vectors_to_upsert = []
            
            for chunk, embedding in zip(chunks, embeddings):
                # Combine chunk metadata with global metadata
                full_metadata = chunk.get("metadata", {})
                if metadata:
                    full_metadata.update(metadata)
                
                vectors_to_upsert.append((
                    chunk["id"],
                    embedding,
                    full_metadata
                ))
            
            # Upsert to Pinecone
            self.index.upsert(vectors=vectors_to_upsert)
            
            logger.info(f"✓ Upserted {len(vectors_to_upsert)} vectors")
            
            # Return document ID (using first chunk's filename)
            doc_id = chunks[0]["filename"] if chunks else "unknown"
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Error upserting vectors: {str(e)}")
            raise
    
    async def search(
        self,
        embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Pinecone
        
        Args:
            embedding: Query embedding vector
            top_k: Number of top results to return
            filter: Metadata filter
        
        Returns:
            List of retrieved documents
        """
        try:
            logger.info(f"🔍 Searching Pinecone for {top_k} similar vectors...")
            
            # Search
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            # Process results
            retrieved_docs = []
            
            for match in results.matches:
                retrieved_docs.append({
                    "id": match.id,
                    "score": float(match.score),
                    "metadata": match.metadata
                })
            
            logger.info(f"✓ Found {len(retrieved_docs)} similar vectors")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"❌ Error searching Pinecone: {str(e)}")
            raise
    
    async def delete_by_metadata(self, filter: Dict[str, Any]) -> int:
        """
        Delete vectors by metadata filter
        
        Args:
            filter: Metadata filter
        
        Returns:
            Number of deleted vectors
        """
        try:
            logger.info(f"🗑️ Deleting vectors with filter: {filter}")
            
            # Delete
            delete_response = self.index.delete(filter=filter)
            
            logger.info(f"✓ Deleted vectors")
            return delete_response.deleted_count if hasattr(delete_response, 'deleted_count') else 0
            
        except Exception as e:
            logger.error(f"❌ Error deleting vectors: {str(e)}")
            raise
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimensions": stats.dimension,
                "index_size_bytes": stats.index_size_bytes
            }
        except Exception as e:
            logger.error(f"❌ Error getting index stats: {str(e)}")
            return {"error": str(e)}