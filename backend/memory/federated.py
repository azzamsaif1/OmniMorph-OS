"""Federated Learning Engine — P2P skill transfer without sharing code.

Manages a decentralised network where users exchange abstract Skill Diffs
via WebRTC data channels.  No raw code or personal data ever leaves the
local node (Feature 2 / Feature 15).
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from typing import Any

from backend.memory.skill_diff import SkillDiff
from backend.utils.logger import log
from backend.utils.security import anonymise_user_id


@dataclass
class PeerInfo:
    peer_id: str
    anon_id: str
    skills: list[str] = field(default_factory=list)
    last_seen: float = 0.0


@dataclass
class FederatedMessage:
    """Envelope for P2P messages."""

    msg_type: str  # "offer_diff" | "request_diff" | "peer_hello" | "peer_bye"
    sender_anon: str
    payload: dict[str, Any] = field(default_factory=dict)
    msg_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


class FederatedNetwork:
    """Manages the peer-to-peer skill-sharing network.

    MVP uses a simple in-memory registry; production replaces with
    WebRTC signaling via ``aiortc``.
    """

    def __init__(self) -> None:
        self._peers: dict[str, PeerInfo] = {}
        self._skill_pool: dict[str, SkillDiff] = {}
        self._message_queue: asyncio.Queue[FederatedMessage] = asyncio.Queue()

    # -- Peer management ---------------------------------------------------

    def register_peer(self, user_id: str, skills: list[str] | None = None) -> str:
        anon = anonymise_user_id(user_id)
        peer = PeerInfo(
            peer_id=uuid.uuid4().hex[:8],
            anon_id=anon,
            skills=skills or [],
        )
        self._peers[anon] = peer
        log.info("federated.peer_registered", anon=anon)
        return peer.peer_id

    def remove_peer(self, user_id: str) -> None:
        anon = anonymise_user_id(user_id)
        self._peers.pop(anon, None)

    def list_peers(self) -> list[PeerInfo]:
        return list(self._peers.values())

    # -- Skill Diff sharing ------------------------------------------------

    def offer_skill_diff(self, diff: SkillDiff) -> None:
        self._skill_pool[diff.diff_id] = diff
        log.info("federated.diff_offered", id=diff.diff_id, domain=diff.skill_domain)

    def search_diffs(self, domain: str, top_k: int = 5) -> list[SkillDiff]:
        matches = [
            d for d in self._skill_pool.values()
            if domain.lower() in d.skill_domain.lower()
        ]
        return sorted(matches, key=lambda d: d.difficulty)[:top_k]

    def get_diff(self, diff_id: str) -> SkillDiff | None:
        return self._skill_pool.get(diff_id)

    # -- Messaging ---------------------------------------------------------

    async def send(self, message: FederatedMessage) -> None:
        await self._message_queue.put(message)

    async def receive(self, timeout: float = 5.0) -> FederatedMessage | None:
        try:
            return await asyncio.wait_for(self._message_queue.get(), timeout)
        except asyncio.TimeoutError:
            return None

    def stats(self) -> dict[str, int]:
        return {
            "peers": len(self._peers),
            "skill_diffs": len(self._skill_pool),
            "queue_size": self._message_queue.qsize(),
        }
