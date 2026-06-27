"""
URL fetcher module
Handles web scraping and URL content extraction
"""

import logging
from typing import Dict, Any, List
import uuid
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class URLFetcher:
    """Fetch and process content from URLs"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, timeout: int = 10):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.timeout = timeout
    
    def fetch_and_process(self, url: str, name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch URL content and return chunks
        
        Args:
            url: URL to fetch
            name: Optional custom name for the source
        
        Returns:
            List of chunks with metadata
        """
        try:
            logger.info(f"📥 Fetching URL: {url}")
            
            # Fetch webpage
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Extract text
            text = self._extract_text(response.content)
            
            if not text or len(text.strip()) < 50:
                logger.warning(f"⚠️ No meaningful content extracted from {url}")
                return []
            
            # Create document name
            doc_name = name or self._get_page_title(response.content) or urlparse(url).netloc
            
            # Chunk the content
            chunks = self._chunk_text(text, doc_name, url)
            
            logger.info(f"✓ Processed URL {url}: {len(chunks)} chunks")
            return chunks
            
        except requests.RequestException as e:
            logger.error(f"❌ Error fetching URL {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error processing URL {url}: {str(e)}")
            raise
    
    def _extract_text(self, content: bytes) -> str:
        """Extract readable text from HTML"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise
    
    def _get_page_title(self, content: bytes) -> Optional[str]:
        """Extract page title from HTML"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.find('title')
            return title.string if title else None
        except:
            return None
    
    def _chunk_text(self, text: str, doc_name: str, source_url: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        chunks = []
        
        # Split into chunks with overlap
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i:i + self.chunk_size]
            
            if len(chunk_text.strip()) > 50:
                chunk_id = str(uuid.uuid4())
                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "filename": doc_name,
                    "metadata": {
                        "chunk_index": len(chunks),
                        "source": doc_name,
                        "source_url": source_url,
                        "file_type": "url"
                    }
                })
        
        return chunks