"""Vector Store — Qdrant client for behavioural fingerprints.

Stores user embedding vectors (1024-d) representing coding style,
error patterns, and decision history.  Supports similarity search
to recall relevant past states and skill profiles.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from backend.config import settings
from backend.utils.logger import log


@dataclass
class VectorRecord:
    id: str
    vector: list[float]
    payload: dict[str, Any]
    score: float = 0.0


class VectorStore:
    """Manages the Qdrant collection for UCSK fingerprints."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        collection: str | None = None,
        dim: int | None = None,
    ) -> None:
        self._host = host or settings.qdrant_host
        self._port = port or settings.qdrant_port
        self._collection = collection or settings.qdrant_collection
        self._dim = dim or settings.qdrant_embedding_dim
        self._client: QdrantClient | None = None

    def connect(self) -> None:
        self._client = QdrantClient(host=self._host, port=self._port)
        collections = [c.name for c in self._client.get_collections().collections]
        if self._collection not in collections:
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(
                    size=self._dim, distance=Distance.COSINE
                ),
            )
            log.info("qdrant.collection_created", name=self._collection)
        log.info("qdrant.connected", host=self._host, port=self._port)

    def upsert(
        self,
        vector: list[float],
        payload: dict[str, Any],
        record_id: str | None = None,
    ) -> str:
        assert self._client is not None, "Call connect() first"
        rid = record_id or uuid.uuid4().hex
        self._client.upsert(
            collection_name=self._collection,
            points=[
                PointStruct(id=rid, vector=vector, payload=payload),
            ],
        )
        log.debug("qdrant.upsert", id=rid)
        return rid

    def search(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[VectorRecord]:
        assert self._client is not None, "Call connect() first"
        results = self._client.search(
            collection_name=self._collection,
            query_vector=query_vector,
            limit=top_k,
        )
        return [
            VectorRecord(
                id=str(r.id),
                vector=r.vector or [],
                payload=r.payload or {},
                score=r.score,
            )
            for r in results
        ]

    def get(self, record_id: str) -> VectorRecord | None:
        assert self._client is not None
        points = self._client.retrieve(
            collection_name=self._collection,
            ids=[record_id],
            with_vectors=True,
        )
        if not points:
            return None
        p = points[0]
        return VectorRecord(
            id=str(p.id),
            vector=p.vector or [],
            payload=p.payload or {},
        )

    def delete(self, record_id: str) -> None:
        assert self._client is not None
        self._client.delete(
            collection_name=self._collection,
            points_selector=[record_id],
        )

    def close(self) -> None:
        self._client = None
