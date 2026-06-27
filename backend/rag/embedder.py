"""
Embedding pipeline module
Converts text to vector embeddings using OpenAI API
"""

import logging
from typing import List, Dict, Any
import asyncio
from openai import AsyncOpenAI
from config import Config

logger = logging.getLogger(__name__)

class EmbeddingPipeline:
    """Generate embeddings for text chunks"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.EMBEDDING_MODEL
        self.embedding_dim = 1536  # text-embedding-3-small dimension
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                return []
            
            logger.info(f"🔄 Embedding {len(texts)} text chunks...")
            
            # Batch embeddings (OpenAI allows up to 100 texts per request)
            embeddings = []
            batch_size = 100
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                logger.info(f"✓ Embedded batch {i//batch_size + 1}: {len(batch)} texts")
            
            logger.info(f"✓ Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {str(e)}")
            raise
    
    async def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for single text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=[text]
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"❌ Error embedding text: {str(e)}")
            raise
    
    async def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Embed document chunks and add embeddings to metadata
        
        Args:
            chunks: List of chunk dictionaries
        
        Returns:
            Chunks with embeddings added
        """
        try:
            # Extract texts
            texts = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings
            embeddings = await self.embed_texts(texts)
            
            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding
            
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Error embedding chunks: {str(e)}")
            raise