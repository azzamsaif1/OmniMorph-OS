"""Gemini API Client — centralized access to Google Gemini.

Provides a singleton async client for all Gemini calls across UCSK.
Falls back to local heuristics when API key is not configured.
"""

from __future__ import annotations

import os
from typing import Any

from backend.utils.logger import log

_GEMINI_MODEL = "gemini-2.0-flash"
_client = None


def _get_client():
    """Return a cached genai.Client singleton."""
    global _client
    if _client is None:
        from google import genai
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        _client = genai.Client(api_key=api_key)
    return _client


async def gemini_generate(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """Generate text via Google Gemini API.

    Falls back to a placeholder if GOOGLE_API_KEY is not set.
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        log.debug("gemini.no_api_key", msg="Returning placeholder response")
        return f"[Gemini placeholder] Response for: {prompt[:100]}..."

    try:
        from google import genai

        client = _get_client()
        config = genai.types.GenerateContentConfig(
            system_instruction=system_instruction or None,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response = await client.aio.models.generate_content(
            model=_GEMINI_MODEL,
            contents=prompt,
            config=config,
        )
        return response.text or ""
    except Exception as exc:
        log.warning("gemini.generate_failed", error=str(exc))
        return f"[Gemini error] {exc}"


async def gemini_analyze_code(
    code: str,
    task: str = "review",
    language: str = "python",
) -> dict[str, Any]:
    """Analyze code using Gemini — returns structured suggestions."""
    system = (
        "You are UCSK's code analysis agent. Respond in JSON with keys: "
        '"summary", "issues" (list of {severity, line, message}), '
        '"suggestions" (list of strings), "quality_score" (0-100).'
    )
    prompt = f"Task: {task}\nLanguage: {language}\n\nCode:\n```{language}\n{code}\n```"
    raw = await gemini_generate(prompt, system_instruction=system, temperature=0.3)

    try:
        import json
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(clean)
    except Exception:
        return {
            "summary": raw[:500],
            "issues": [],
            "suggestions": [],
            "quality_score": 70,
        }


async def gemini_generate_scenario(
    domain: str,
    difficulty: str,
    skills: list[str],
    user_level: str = "intermediate",
) -> dict[str, Any]:
    """Generate a training scenario dynamically via Gemini."""
    system = (
        "You are UCSK's training scenario generator. Create a complete engineering "
        "project scenario. Respond in JSON with keys: "
        '"title", "description", "skills" (list), "difficulty", '
        '"estimated_hours" (int), "milestones" (list of strings), '
        '"starter_code" (optional string).'
    )
    prompt = (
        f"Generate a {difficulty} difficulty training scenario for a {user_level} "
        f"engineer in the {domain} domain. Target skills: {', '.join(skills)}. "
        f"The scenario should be a complete, real-world engineering project."
    )
    raw = await gemini_generate(prompt, system_instruction=system, temperature=0.8)

    try:
        import json
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(clean)
    except Exception:
        return {
            "title": f"Dynamic {domain} Scenario",
            "description": raw[:500],
            "skills": skills,
            "difficulty": difficulty,
            "estimated_hours": 4,
            "milestones": ["Analyze requirements", "Implement solution", "Write tests"],
        }


async def gemini_career_advice(
    capability_profile: dict[str, Any],
    current_role: str = "developer",
) -> dict[str, Any]:
    """Generate career path recommendations via Gemini."""
    system = (
        "You are UCSK's career advisor. Based on the capability profile, suggest career paths. "
        "Respond in JSON with keys: "
        '"current_assessment", "paths" (list of {title, description, timeline, fit_score, skills_needed}), '
        '"immediate_actions" (list of strings).'
    )
    prompt = (
        f"Current role: {current_role}\n"
        f"Capability profile: {capability_profile}\n"
        f"Suggest 3 career paths with fit scores."
    )
    raw = await gemini_generate(prompt, system_instruction=system, temperature=0.6)

    try:
        import json
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(clean)
    except Exception:
        return {
            "current_assessment": "Analysis pending",
            "paths": [],
            "immediate_actions": ["Continue building skills"],
        }


async def gemini_guidance(
    mental_state: str,
    work_context: dict[str, Any],
    query: str = "",
) -> str:
    """Generate real-time guidance for the user based on context."""
    system = (
        "You are UCSK, an AI cognitive assistant. Provide brief, actionable guidance "
        "based on the user's mental state and work context. Be concise (2-3 sentences max)."
    )
    prompt = (
        f"Mental state: {mental_state}\n"
        f"Active file: {work_context.get('active_file', 'unknown')}\n"
        f"Recent actions: {work_context.get('recent_actions', [])}\n"
    )
    if query:
        prompt += f"\nUser question: {query}"
    else:
        prompt += "\nProvide a contextual suggestion."

    return await gemini_generate(prompt, system_instruction=system, temperature=0.5, max_tokens=256)
