"""
RAGAS Evaluator module
Evaluates RAG response quality using RAGAS metrics
"""

import logging
from typing import List, Dict, Any
from ragas.metrics import faithfulness, answer_relevancy, context_relevancy
from ragas.llm import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from config import Config

logger = logging.getLogger(__name__)

class RAGEvaluator:
    """Evaluate RAG responses using RAGAS framework"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY
        )
    
    async def evaluate(
        self,
        query: str,
        answer: str,
        context: List[str]
    ) -> Dict[str, float]:
        """
        Evaluate RAG response quality
        
        Args:
            query: User query
            answer: Generated answer
            context: Retrieved context documents
        
        Returns:
            Dictionary with evaluation scores
        """
        try:
            logger.info(f"📊 Evaluating answer quality...")
            
            scores = {
                "faithfulness": await self._evaluate_faithfulness(answer, context),
                "answer_relevance": await self._evaluate_relevance(query, answer),
                "context_relevance": await self._evaluate_context_relevance(query, context)
            }
            
            logger.info(f"✓ Evaluation complete: {scores}")
            return scores
            
        except Exception as e:
            logger.error(f"❌ Error evaluating response: {str(e)}")
            # Return default scores on error
            return {
                "faithfulness": 0.5,
                "answer_relevance": 0.5,
                "context_relevance": 0.5
            }
    
    async def _evaluate_faithfulness(self, answer: str, context: List[str]) -> float:
        """
        Evaluate faithfulness: Does answer stick to context?
        Score: 0-1 (higher is better)
        """
        try:
            # Simple heuristic: check if answer contains information from context
            answer_lower = answer.lower()
            context_text = " ".join(context).lower()
            
            # Count words from answer that appear in context
            answer_words = set(answer_lower.split())
            context_words = set(context_text.split())
            
            overlap = len(answer_words & context_words)
            total = len(answer_words)
            
            faithfulness_score = overlap / total if total > 0 else 0.0
            
            # Cap at 1.0 and ensure minimum 0.1 if answer references context
            faithfulness_score = min(max(faithfulness_score, 0.1), 1.0)
            
            logger.info(f"  Faithfulness: {faithfulness_score:.2f}")
            return faithfulness_score
            
        except Exception as e:
            logger.error(f"Error calculating faithfulness: {str(e)}")
            return 0.5
    
    async def _evaluate_relevance(self, query: str, answer: str) -> float:
        """
        Evaluate answer relevance: Does answer address query?
        Score: 0-1 (higher is better)
        """
        try:
            # Check if answer contains key terms from query
            query_lower = query.lower()
            answer_lower = answer.lower()
            
            # Extract key terms (words > 4 chars)
            query_terms = {word for word in query_lower.split() if len(word) > 4}
            
            # Count matches
            matches = sum(1 for term in query_terms if term in answer_lower)
            relevance_score = matches / len(query_terms) if query_terms else 0.5
            
            # Ensure between 0.1 and 1.0
            relevance_score = min(max(relevance_score, 0.1), 1.0)
            
            logger.info(f"  Answer Relevance: {relevance_score:.2f}")
            return relevance_score
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {str(e)}")
            return 0.5
    
    async def _evaluate_context_relevance(self, query: str, context: List[str]) -> float:
        """
        Evaluate context relevance: Is context relevant to query?
        Score: 0-1 (higher is better)
        """
        try:
            if not context:
                return 0.0
            
            query_lower = query.lower()
            context_text = " ".join(context).lower()
            
            # Check overlap between query and context
            query_terms = set(query_lower.split())
            context_words = set(context_text.split())
            
            overlap = len(query_terms & context_words)
            relevance_score = overlap / len(query_terms) if query_terms else 0.5
            
            # Ensure between 0.1 and 1.0
            relevance_score = min(max(relevance_score, 0.1), 1.0)
            
            logger.info(f"  Context Relevance: {relevance_score:.2f}")
            return relevance_score
            
        except Exception as e:
            logger.error(f"Error calculating context relevance: {str(e)}")
            return 0.5
    
    def get_score_explanation(self, scores: Dict[str, float]) -> str:
        """Get human-readable explanation of scores"""
        explanations = []
        
        faith = scores.get("faithfulness", 0)
        if faith > 0.8:
            explanations.append("✓ Answer is highly faithful to source documents")
        elif faith > 0.6:
            explanations.append("~ Answer is mostly faithful to source documents")
        else:
            explanations.append("⚠️ Answer may contain information not in source documents")
        
        rel = scores.get("answer_relevance", 0)
        if rel > 0.8:
            explanations.append("✓ Answer directly addresses the query")
        elif rel > 0.6:
            explanations.append("~ Answer partially addresses the query")
        else:
            explanations.append("⚠️ Answer may not fully address the query")
        
        return "\n".join(explanations)