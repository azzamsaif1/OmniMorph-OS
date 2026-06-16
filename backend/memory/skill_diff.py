"""Skill Diff — generates transferable skill abstractions via Gemini.

Converts a user's demonstrated expertise into an anonymised, abstract
"Skill Diff" that can be transferred to other users without sharing
any raw code or personal data (Feature 2 / Feature 15).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.config import settings
from backend.utils.logger import log
from backend.utils.security import anonymise_user_id


@dataclass
class SkillDiff:
    """A portable, privacy-safe knowledge delta."""

    diff_id: str
    source_anon_id: str
    skill_domain: str
    abstraction: str       # Natural-language skill description
    exercises: list[str]   # Generated practice prompts
    difficulty: float      # 0..1
    metadata: dict[str, Any]


async def _call_gemini(prompt: str) -> str:
    """Call Google Gemini API for skill abstraction."""
    from google import genai

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
    )
    return response.text or ""


class SkillDiffGenerator:
    """Creates anonymous Skill Diffs from user performance data."""

    async def generate(
        self,
        user_id: str,
        skill_domain: str,
        evidence: str,
        difficulty: float = 0.5,
    ) -> SkillDiff:
        """Produce a Skill Diff from raw evidence (code patterns, errors, etc.)."""
        anon_id = anonymise_user_id(user_id)

        prompt = (
            f"You are an expert programming tutor. A developer has demonstrated "
            f"proficiency in '{skill_domain}'. Based on the following evidence, "
            f"create:\n"
            f"1. A concise abstraction of the skill (2-3 sentences).\n"
            f"2. Three practice exercises of difficulty {difficulty:.1f}/1.0 that "
            f"would help another developer acquire this skill.\n\n"
            f"Evidence:\n{evidence}\n\n"
            f"IMPORTANT: Do NOT include any personally identifiable information, "
            f"variable names, or proprietary code in your response."
        )

        try:
            raw = await _call_gemini(prompt)
        except Exception as exc:
            log.warning("skill_diff.gemini_error", error=str(exc))
            raw = (
                f"Skill: {skill_domain}\n"
                f"Abstraction: Demonstrated competence in {skill_domain}.\n"
                f"Exercise 1: Implement a basic {skill_domain} example.\n"
                f"Exercise 2: Debug a common {skill_domain} mistake.\n"
                f"Exercise 3: Optimise a {skill_domain} solution."
            )

        # Parse the response into structured fields
        lines = raw.strip().split("\n")
        abstraction = lines[0] if lines else f"Skill in {skill_domain}"
        exercises = [l.strip("- ") for l in lines[1:] if l.strip()][:3]

        import uuid

        diff = SkillDiff(
            diff_id=uuid.uuid4().hex[:16],
            source_anon_id=anon_id,
            skill_domain=skill_domain,
            abstraction=abstraction,
            exercises=exercises or [f"Practice {skill_domain}"],
            difficulty=difficulty,
            metadata={"model": settings.gemini_model},
        )
        log.info("skill_diff.generated", domain=skill_domain, diff_id=diff.diff_id)
        return diff

    async def apply(self, diff: SkillDiff, target_user_id: str) -> dict[str, Any]:
        """Apply a Skill Diff to a target user (returns tailored exercises)."""
        prompt = (
            f"A developer (ID: anon) needs to learn: {diff.abstraction}\n"
            f"Adapt the following exercises to their level:\n"
            + "\n".join(f"- {e}" for e in diff.exercises)
            + f"\n\nDifficulty target: {diff.difficulty:.1f}/1.0"
        )
        try:
            tailored = await _call_gemini(prompt)
        except Exception:
            tailored = "\n".join(diff.exercises)

        return {
            "diff_id": diff.diff_id,
            "target_user": anonymise_user_id(target_user_id),
            "tailored_exercises": tailored,
        }
