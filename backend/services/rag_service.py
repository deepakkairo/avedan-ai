"""
services/rag_service.py – ChromaDB RAG Service for Scheme Search
================================================================
Handles vector embeddings and semantic search for government schemes.

Architecture:
  - ChromaDB stores embeddings of scheme text (name + description +
    eligibility + documents + ministry + state).
  - OpenAI text-embedding-3-small is used for embedding generation.
  - Semantic search is the primary discovery method; structured
    filters (state) narrow results.
"""

import json
import logging
from typing import Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings

from config import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# ChromaDB Client & Collection
# ─────────────────────────────────────────────────────────────────────────────

_chroma_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None
_embeddings: Optional[OpenAIEmbeddings] = None

COLLECTION_NAME = "schemes"


def _get_embeddings() -> OpenAIEmbeddings:
    """Lazily initialize the OpenAI embeddings model."""
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key,
        )
    return _embeddings


def get_chroma_client() -> chromadb.PersistentClient:
    """Return (or initialize) the ChromaDB persistent client."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info("ChromaDB client initialized at: %s", settings.chroma_persist_dir)
    return _chroma_client


def get_collection() -> chromadb.Collection:
    """Return (or create) the 'schemes' collection in ChromaDB."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # cosine similarity for search
        )
        logger.info(
            "ChromaDB collection '%s' ready (%d documents).",
            COLLECTION_NAME,
            _collection.count(),
        )
    return _collection


def _build_document_text(scheme: dict[str, Any]) -> str:
    """
    Combine scheme fields into a single text string for embedding.
    This rich text improves semantic search quality.
    """
    docs = scheme.get("documents_required", [])
    if isinstance(docs, list):
        docs_str = ", ".join(docs)
    else:
        docs_str = str(docs)

    return (
        f"Scheme Name: {scheme.get('name', '')}\n"
        f"Ministry: {scheme.get('ministry', '')}\n"
        f"State: {scheme.get('state', 'central')}\n"
        f"Description: {scheme.get('description', '')}\n"
        f"Eligibility: {scheme.get('eligibility', '')}\n"
        f"Documents Required: {docs_str}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def add_scheme(scheme: dict[str, Any]) -> None:
    """
    Embed a scheme and add (or update) it in ChromaDB.

    Args:
        scheme: Dict with keys matching the Scheme model fields.
                Must include 'id' as the document identifier.

    Raises:
        ValueError: If 'id' is missing from scheme dict.
    """
    scheme_id = scheme.get("id")
    if not scheme_id:
        raise ValueError("Scheme dict must have an 'id' field.")

    collection = get_collection()
    embeddings_model = _get_embeddings()

    # Build the text that will be embedded
    document_text = _build_document_text(scheme)

    # Generate embedding vector
    try:
        embedding_vector = embeddings_model.embed_query(document_text)
    except Exception as exc:
        logger.error("Failed to embed scheme %s: %s", scheme_id, exc)
        raise

    # Metadata stored alongside embedding for filtering
    metadata = {
        "name": scheme.get("name", ""),
        "ministry": scheme.get("ministry", "") or "",
        "state": scheme.get("state", "central"),
        "official_url": scheme.get("official_url", ""),
        "has_api": str(scheme.get("has_api", False)),
        "fee_amount": str(scheme.get("fee_amount") or "free"),
    }

    # Upsert: add if new, update if exists
    collection.upsert(
        ids=[scheme_id],
        embeddings=[embedding_vector],
        documents=[document_text],
        metadatas=[metadata],
    )
    logger.debug("Scheme upserted to ChromaDB: %s", scheme_id)


def search_schemes(
    query: str,
    n_results: int = 5,
    state_filter: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Semantic search across all schemes in ChromaDB.

    Args:
        query: Natural language query e.g. "housing scheme for farmers BPL".
        n_results: Maximum number of results to return.
        state_filter: If provided, restrict to schemes matching this state
                      (case-insensitive) or 'central'.

    Returns:
        List of dicts with keys: id, name, ministry, state, official_url,
        has_api, fee_amount, distance, document (embedded text).
    """
    collection = get_collection()
    embeddings_model = _get_embeddings()

    if collection.count() == 0:
        logger.warning("ChromaDB collection is empty. Run init_db.py first.")
        return []

    # Embed the query
    try:
        query_embedding = embeddings_model.embed_query(query)
    except Exception as exc:
        logger.error("Failed to embed search query: %s", exc)
        raise

    # Build optional where filter for state
    where_filter = None
    if state_filter:
        normalized = state_filter.strip().lower()
        if normalized == "central":
            where_filter = {"state": {"$eq": "central"}}
        else:
            # Match exact state name (case stored as-is during seed)
            where_filter = {
                "$or": [
                    {"state": {"$eq": state_filter}},
                    {"state": {"$eq": "central"}},
                ]
            }

    # Query ChromaDB
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count()),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        logger.error("ChromaDB query failed: %s", exc)
        raise

    # Format results
    formatted: list[dict[str, Any]] = []
    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    documents = results.get("documents", [[]])[0]

    for idx, scheme_id in enumerate(ids):
        meta = metadatas[idx] if idx < len(metadatas) else {}
        dist = distances[idx] if idx < len(distances) else 1.0
        doc = documents[idx] if idx < len(documents) else ""

        # Convert cosine distance to similarity score (0–1, higher is better)
        similarity = round(1 - dist, 4)

        formatted.append(
            {
                "id": scheme_id,
                "name": meta.get("name", ""),
                "ministry": meta.get("ministry", ""),
                "state": meta.get("state", "central"),
                "official_url": meta.get("official_url", ""),
                "has_api": meta.get("has_api", "False") == "True",
                "fee_amount": meta.get("fee_amount", "free"),
                "match_score": similarity,
                "document": doc,
            }
        )

    logger.info(
        "Search '%s' (state=%s) → %d results", query, state_filter, len(formatted)
    )
    return formatted


def get_scheme_by_id(scheme_id: str) -> Optional[dict[str, Any]]:
    """
    Retrieve a specific scheme from ChromaDB by its ID.

    Returns:
        Scheme dict or None if not found.
    """
    collection = get_collection()
    try:
        result = collection.get(
            ids=[scheme_id],
            include=["documents", "metadatas"],
        )
    except Exception as exc:
        logger.error("Failed to get scheme %s: %s", scheme_id, exc)
        return None

    ids = result.get("ids", [])
    if not ids:
        return None

    metadatas = result.get("metadatas", [{}])
    documents = result.get("documents", [""])
    meta = metadatas[0] if metadatas else {}

    return {
        "id": ids[0],
        "name": meta.get("name", ""),
        "ministry": meta.get("ministry", ""),
        "state": meta.get("state", "central"),
        "official_url": meta.get("official_url", ""),
        "has_api": meta.get("has_api", "False") == "True",
        "fee_amount": meta.get("fee_amount", "free"),
        "document": documents[0] if documents else "",
    }


def count_schemes() -> int:
    """Return total number of schemes stored in ChromaDB."""
    try:
        return get_collection().count()
    except Exception as exc:
        logger.error("Failed to count schemes: %s", exc)
        return 0


def delete_scheme(scheme_id: str) -> bool:
    """
    Remove a scheme from ChromaDB by ID.

    Returns:
        True if deleted, False if not found or error.
    """
    collection = get_collection()
    try:
        collection.delete(ids=[scheme_id])
        logger.info("Scheme deleted from ChromaDB: %s", scheme_id)
        return True
    except Exception as exc:
        logger.error("Failed to delete scheme %s: %s", scheme_id, exc)
        return False


def initialize_chromadb() -> None:
    """
    Initialize ChromaDB at application startup.
    Called from FastAPI lifespan. Safe to call multiple times.
    """
    try:
        collection = get_collection()
        logger.info(
            "ChromaDB initialized. Collection '%s' has %d schemes.",
            COLLECTION_NAME,
            collection.count(),
        )
    except Exception as exc:
        logger.critical("Failed to initialize ChromaDB: %s", exc)
        raise
