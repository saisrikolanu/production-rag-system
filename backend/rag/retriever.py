"""
RAG Retriever module
Orchestrates retrieval and LLM-based answer generation
"""

import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI
from rag.embedder import EmbeddingPipeline
from rag.pinecone_handler import PineconeHandler
from config import Config

logger = logging.getLogger(__name__)

class RAGRetriever:
    """Retrieve documents and generate answers using RAG"""
    
    def __init__(
        self,
        pinecone: PineconeHandler,
        embedder: EmbeddingPipeline,
        config: Config
    ):
        self.pinecone = pinecone
        self.embedder = embedder
        self.config = config
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
        
        Returns:
            List of retrieved documents with scores
        """
        try:
            logger.info(f"📚 Retrieving documents for query: {query}")
            
            # Embed query
            query_embedding = await self.embedder.embed_single(query)
            
            # Search Pinecone
            search_results = await self.pinecone.search(
                embedding=query_embedding,
                top_k=top_k
            )
            
            if not search_results:
                logger.warning("⚠️ No documents found")
                return []
            
            # Reconstruct document information
            retrieved_docs = []
            for result in search_results:
                retrieved_docs.append({
                    "id": result["id"],
                    "filename": result["metadata"].get("source", "Unknown"),
                    "text": result["metadata"].get("text", ""),
                    "score": result["score"],
                    "metadata": result["metadata"]
                })
            
            logger.info(f"✓ Retrieved {len(retrieved_docs)} documents")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"❌ Error retrieving documents: {str(e)}")
            raise
    
    async def generate_answer(
        self,
        query: str,
        context_docs: List[Dict[str, Any]]
    ) -> str:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User query
            context_docs: Retrieved context documents
        
        Returns:
            Generated answer
        """
        try:
            logger.info(f"🤖 Generating answer for query: {query}")
            
            # Build context string
            context_text = "\n\n".join([
                f"Document: {doc['filename']}\n{doc['text']}"
                for doc in context_docs
            ])
            
            # Limit context to avoid token overflow
            if len(context_text) > self.config.MAX_CONTEXT_LENGTH:
                context_text = context_text[:self.config.MAX_CONTEXT_LENGTH] + "..."
            
            # Create prompt
            prompt = f"""You are a helpful assistant. Answer the following question based on the provided documents.

Documents:
{context_text}

Question: {query}

Answer:"""
            
            # Generate answer
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided documents. Be accurate and cite sources when relevant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            logger.info(f"✓ Generated answer ({len(answer)} chars)")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error generating answer: {str(e)}")
            raise
    
    async def query(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve and generate
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
        
        Returns:
            Query result with answer and sources
        """
        try:
            # Retrieve documents
            retrieved_docs = await self.retrieve(query, top_k)
            
            if not retrieved_docs:
                return {
                    "query": query,
                    "answer": "No relevant documents found.",
                    "sources": []
                }
            
            # Generate answer
            answer = await self.generate_answer(query, retrieved_docs)
            
            return {
                "query": query,
                "answer": answer,
                "sources": [
                    {
                        "filename": doc["filename"],
                        "text": doc["text"][:200] + "...",
                        "score": doc["score"]
                    }
                    for doc in retrieved_docs
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error in RAG query: {str(e)}")
            raise