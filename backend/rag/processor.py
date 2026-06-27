"""
Document processing module
Handles PDF, TXT, and DOCX file processing and chunking
"""

import logging
from typing import List, Dict, Any
from pathlib import Path
import uuid
import PyPDF2
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process documents into chunks for RAG"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process(
        self, 
        filename: str, 
        content: bytes, 
        file_type: str
    ) -> List[Dict[str, Any]]:
        """
        Process document and return chunks
        
        Args:
            filename: Name of the file
            content: File content (bytes)
            file_type: File type (pdf, txt, docx)
        
        Returns:
            List of chunks with metadata
        """
        try:
            # Extract text based on file type
            if file_type.lower() == 'pdf':
                text = self._extract_pdf(content)
            elif file_type.lower() == 'txt':
                text = content.decode('utf-8')
            elif file_type.lower() == 'docx':
                text = self._extract_docx(content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Split into chunks
            chunks = self._chunk_text(text, filename)
            
            logger.info(f"✓ Processed {filename}: {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Error processing {filename}: {str(e)}")
            raise
    
    def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            from io import BytesIO
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise
    
    def _extract_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            from io import BytesIO
            doc = DocxDocument(BytesIO(content))
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX: {str(e)}")
            raise
    
    def _chunk_text(self, text: str, filename: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        chunks = []
        
        # Clean text
        text = text.strip()
        
        # Split into chunks with overlap
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i:i + self.chunk_size]
            
            if len(chunk_text.strip()) > 50:  # Only include non-empty chunks
                chunk_id = str(uuid.uuid4())
                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "filename": filename,
                    "metadata": {
                        "chunk_index": len(chunks),
                        "source": filename,
                        "file_type": filename.split(".")[-1]
                    }
                })
        
        return chunks