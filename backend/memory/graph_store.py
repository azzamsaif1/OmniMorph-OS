"""Graph Store — Neo4j client for cognitive relationships.

Models relationships between concepts, skills, errors, and decisions
as a knowledge graph that powers the Digital Twin (Feature 11).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from neo4j import AsyncGraphDatabase, AsyncDriver

from backend.config import settings
from backend.utils.logger import log


@dataclass
class GraphNode:
    id: str
    labels: list[str]
    properties: dict[str, Any]


@dataclass
class GraphRelation:
    source_id: str
    target_id: str
    relation_type: str
    properties: dict[str, Any]


class GraphStore:
    """Async Neo4j wrapper for the UCSK cognitive graph."""

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self._uri = uri or settings.neo4j_uri
        self._user = user or settings.neo4j_user
        self._password = password or settings.neo4j_password
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        self._driver = AsyncGraphDatabase.driver(
            self._uri, auth=(self._user, self._password)
        )
        log.info("neo4j.connected", uri=self._uri)

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def create_node(
        self, label: str, properties: dict[str, Any]
    ) -> str:
        assert self._driver is not None
        async with self._driver.session() as session:
            result = await session.run(
                f"CREATE (n:{label} $props) RETURN elementId(n) AS id",
                props=properties,
            )
            record = await result.single()
            node_id = record["id"] if record else ""
            log.debug("neo4j.node_created", label=label, id=node_id)
            return str(node_id)

    async def create_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        assert self._driver is not None
        props = properties or {}
        async with self._driver.session() as session:
            await session.run(
                f"""
                MATCH (a) WHERE elementId(a) = $src
                MATCH (b) WHERE elementId(b) = $tgt
                CREATE (a)-[r:{relation_type} $props]->(b)
                """,
                src=source_id,
                tgt=target_id,
                props=props,
            )
            log.debug("neo4j.relation_created", type=relation_type)

    async def query(self, cypher: str, **params: Any) -> list[dict[str, Any]]:
        assert self._driver is not None
        async with self._driver.session() as session:
            result = await session.run(cypher, **params)
            records = [dict(r) async for r in result]
            return records

    async def get_user_skill_graph(self, user_id: str) -> list[dict[str, Any]]:
        return await self.query(
            """
            MATCH (u:User {user_id: $uid})-[r]->(s:Skill)
            RETURN s.name AS skill, type(r) AS relation, r.level AS level
            ORDER BY r.level DESC
            """,
            uid=user_id,
        )

    async def record_error_pattern(
        self, user_id: str, error_type: str, context: str
    ) -> str:
        return await self.create_node(
            "ErrorPattern",
            {
                "user_id": user_id,
                "error_type": error_type,
                "context": context,
            },
        )
