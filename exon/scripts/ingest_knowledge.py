"""
File: /opt/futureex/exon/scripts/ingest_knowledge.py
Author: Ashish Pal
Purpose: Ingest Markdown knowledge files into Exon's vector database.
Usage: 
    python -m exon.scripts.ingest_knowledge
    python -m exon.scripts.ingest_knowledge --dir /path/to/markdown/files
    python -m exon.scripts.ingest_knowledge --clear  # Clear existing knowledge first
"""

import sys
import os
import asyncio
import argparse
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import json

import psycopg2
from psycopg2.extras import Json, execute_values
import numpy as np
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================
EXON_ID = os.environ.get("EXON_ID", "EXN-001")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "futureex")
DB_USER = os.environ.get("DB_USER", "futureex")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "futureex123")

# Embedding model (lightweight, 384 dimensions)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chunking settings
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50  # overlap between chunks

# ============================================================================
# Text Chunking
# ============================================================================
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at a sentence boundary
        if end < len(text):
            # Find last period, question mark, or newline within the chunk
            for sep in ['. ', '? ', '! ', '\n\n', '\n', ' ']:
                last_sep = text.rfind(sep, start, end)
                if last_sep > start + chunk_size // 2:
                    end = last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end - overlap > start else end
    
    return chunks


def read_markdown_files(directory: str) -> List[Dict]:
    """Read all markdown files from directory and subdirectories."""
    files_data = []
    md_path = Path(directory)
    
    if not md_path.exists():
        logger.error(f"Directory not found: {directory}")
        return files_data
    
    md_files = list(md_path.rglob("*.md"))
    logger.info(f"Found {len(md_files)} markdown files")
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.strip():
                files_data.append({
                    "filename": str(file_path.relative_to(md_path)),
                    "content": content,
                    "size": len(content)
                })
                logger.info(f"  ✓ {file_path.relative_to(md_path)} ({len(content)} chars)")
            else:
                logger.warning(f"  ⊘ {file_path.relative_to(md_path)} (empty)")
        except Exception as e:
            logger.error(f"  ✗ {file_path}: {e}")
    
    return files_data


# ============================================================================
# Database Operations
# ============================================================================
def get_db_connection():
    """Create PostgreSQL connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def ensure_table_exists(conn):
    """Create knowledge table if it doesn't exist."""
    with conn.cursor() as cur:
        # Enable pgvector
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS exon_knowledge (
                id SERIAL PRIMARY KEY,
                exon_id VARCHAR(50) NOT NULL,
                source_file VARCHAR(255),
                chunk_text TEXT NOT NULL,
                embedding vector(384),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index if not exists
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_embedding 
            ON exon_knowledge 
            USING ivfflat (embedding vector_cosine_ops) 
            WITH (lists = 100);
        """)
        
        conn.commit()
        logger.info("Knowledge table ready")


def clear_knowledge(conn, exon_id: str):
    """Remove all knowledge for this Exon."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM exon_knowledge WHERE exon_id = %s", (exon_id,))
        conn.commit()
        logger.info(f"Cleared existing knowledge for {exon_id}")


def store_embeddings(conn, exon_id: str, chunks: List[Dict]):
    """Store text chunks with embeddings in database."""
    with conn.cursor() as cur:
        # Prepare data for batch insert
        records = []
        for chunk in chunks:
            records.append((
                exon_id,
                chunk["source_file"],
                chunk["text"],
                chunk["embedding"].tolist(),  # Convert numpy array to list
                Json(chunk.get("metadata", {}))
            ))
        
        # Batch insert using execute_values
        execute_values(
            cur,
            """
            INSERT INTO exon_knowledge (exon_id, source_file, chunk_text, embedding, metadata)
            VALUES %s
            """,
            records,
            template="(%s, %s, %s, %s::vector, %s)"
        )
        
        conn.commit()
        logger.info(f"Stored {len(records)} chunks in database")


# ============================================================================
# Main Ingestion Pipeline
# ============================================================================
async def ingest_knowledge(directory: str, clear_first: bool = False):
    """Main ingestion pipeline."""
    logger.info("=" * 60)
    logger.info("EXON KNOWLEDGE INGESTION")
    logger.info("=" * 60)
    
    # 1. Read markdown files
    logger.info("\n📁 Reading markdown files...")
    files_data = read_markdown_files(directory)
    
    if not files_data:
        logger.error("No files to process!")
        return
    
    total_chars = sum(f["size"] for f in files_data)
    logger.info(f"Total content: {total_chars} characters across {len(files_data)} files")
    
    # 2. Chunk texts
    logger.info("\n✂️  Chunking texts...")
    all_chunks = []
    for file_data in files_data:
        chunks = chunk_text(file_data["content"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source_file": file_data["filename"],
                "text": chunk,
                "metadata": {
                    "filename": file_data["filename"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "char_count": len(chunk)
                }
            })
    
    logger.info(f"Created {len(all_chunks)} chunks (avg {total_chars // max(len(all_chunks), 1)} chars/chunk)")
    
    # 3. Generate embeddings
    logger.info(f"\n🧮 Generating embeddings using {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    
    for i, embedding in enumerate(embeddings):
        all_chunks[i]["embedding"] = embedding
    
    logger.info(f"Generated {len(embeddings)} embeddings (dim={embeddings[0].shape[0]})")
    
    # 4. Store in database
    logger.info("\n💾 Storing in PostgreSQL...")
    conn = get_db_connection()
    
    try:
        ensure_table_exists(conn)
        
        if clear_first:
            clear_knowledge(conn, EXON_ID)
        
        store_embeddings(conn, EXON_ID, all_chunks)
        
        logger.info(f"\n✅ Successfully ingested {len(all_chunks)} knowledge chunks!")
        
        # Stats
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*), SUM(char_length(chunk_text)) FROM exon_knowledge WHERE exon_id = %s",
                (EXON_ID,)
            )
            count, total_chars = cur.fetchone()
            logger.info(f"\n📊 Knowledge Base Stats:")
            logger.info(f"   Total chunks: {count}")
            logger.info(f"   Total characters: {total_chars}")
            
            cur.execute(
                "SELECT source_file, COUNT(*) as cnt FROM exon_knowledge WHERE exon_id = %s GROUP BY source_file ORDER BY cnt DESC",
                (EXON_ID,)
            )
            logger.info(f"\n   Files indexed:")
            for row in cur.fetchall():
                logger.info(f"     • {row[0]}: {row[1]} chunks")
    
    finally:
        conn.close()
    
    logger.info("\n" + "=" * 60)
    logger.info("INGESTION COMPLETE")
    logger.info("=" * 60)


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="Ingest Markdown knowledge into Exon")
    parser.add_argument(
        "--dir", "-d",
        default="knowledge",
        help="Directory containing .md files (default: 'knowledge/')"
    )
    parser.add_argument(
        "--clear", "-c",
        action="store_true",
        help="Clear existing knowledge before ingestion"
    )
    parser.add_argument(
        "--exon-id",
        default=EXON_ID,
        help=f"Exon ID (default: {EXON_ID})"
    )
    
    args = parser.parse_args()
    
    # Override EXON_ID if specified
    global EXON_ID
    EXON_ID = args.exon_id
    
    # Resolve directory path
    directory = args.dir
    if not os.path.isabs(directory):
        # Relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        directory = os.path.join(project_root, directory)
    
    logger.info(f"Knowledge directory: {directory}")
    
    asyncio.run(ingest_knowledge(directory, args.clear))


if __name__ == "__main__":
    main()