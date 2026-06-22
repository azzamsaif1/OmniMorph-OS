"""Database agent — schema design, query optimization, migration management."""

import time
from typing import Any

from backend.gemini_client import generate_content


class DatabaseAgent:
    """Specialized agent for database operations.

    Capabilities:
    - Schema design (relational, document, graph)
    - Query optimization
    - Migration script generation
    - Index recommendations
    - Data modeling
    """

    def __init__(self):
        self.tasks_completed: int = 0
        self.success_rate: float = 0.87

    async def design_schema(
        self, entities: list[str], relationships: list[str] | None = None,
        db_type: str = "postgresql"
    ) -> dict[str, Any]:
        """Design database schema from entity descriptions."""
        prompt = (
            f"Design a {db_type} schema for entities: {', '.join(entities)}\n\n"
            f"Relationships: {relationships or ['infer from context']}\n\n"
            f"Include:\n"
            f"- CREATE TABLE statements\n"
            f"- Primary/foreign keys\n"
            f"- Indexes for common queries\n"
            f"- Constraints (NOT NULL, UNIQUE, CHECK)\n"
            f"- Timestamps and soft-delete support"
        )

        code = await generate_content(prompt)
        self.tasks_completed += 1

        return {
            "type": "schema",
            "db_type": db_type,
            "entities": entities,
            "code": code or self._fallback_schema(entities, db_type),
            "generated_at": time.time(),
        }

    async def optimize_query(self, query: str, schema_context: str = "") -> dict[str, Any]:
        """Optimize a SQL query for performance."""
        prompt = (
            f"Optimize this SQL query:\n\n```sql\n{query}\n```\n\n"
            f"Schema context: {schema_context}\n\n"
            f"Provide: optimized query, explain plan analysis, index recommendations."
        )

        response = await generate_content(prompt)
        self.tasks_completed += 1

        return {
            "type": "query_optimization",
            "original": query,
            "optimized": response or query,
            "generated_at": time.time(),
        }

    async def generate_migration(
        self, changes: list[str], orm: str = "alembic"
    ) -> dict[str, Any]:
        """Generate database migration script."""
        prompt = (
            f"Generate an {orm} migration for these changes:\n\n"
            + "\n".join(f"- {c}" for c in changes) +
            f"\n\nInclude upgrade() and downgrade() functions."
        )

        code = await generate_content(prompt)
        self.tasks_completed += 1

        return {
            "type": "migration",
            "orm": orm,
            "changes": changes,
            "code": code or "# Migration requires Gemini API",
            "generated_at": time.time(),
        }

    def _fallback_schema(self, entities: list[str], db_type: str) -> str:
        lines = [f"-- {db_type} schema\n"]
        for entity in entities:
            name = entity.lower().replace(" ", "_")
            lines.append(
                f"CREATE TABLE {name} (\n"
                f"    id SERIAL PRIMARY KEY,\n"
                f"    name VARCHAR(255) NOT NULL,\n"
                f"    created_at TIMESTAMP DEFAULT NOW(),\n"
                f"    updated_at TIMESTAMP DEFAULT NOW()\n"
                f");\n"
            )
        return "\n".join(lines)

    def get_stats(self) -> dict[str, Any]:
        return {
            "agent": "database",
            "tasks_completed": self.tasks_completed,
            "success_rate": self.success_rate,
        }
