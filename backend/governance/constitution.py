"""Constitution — Kernel-Level Ethical Rules.

Defines immutable ethical boundaries that UCSK must never violate.
All system actions are validated against this constitution before execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from backend.utils.logger import log


class ViolationType(str, Enum):
    """Categories of constitutional violations."""

    PRIVACY = "privacy"
    DATA_EXFILTRATION = "data_exfiltration"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CONSENT_MISSING = "consent_missing"
    HARMFUL_ACTION = "harmful_action"
    BIAS_DETECTED = "bias_detected"


@dataclass
class ConstitutionalRule:
    """A single ethical rule in the UCSK constitution."""

    id: str
    name: str
    description: str
    violation_type: ViolationType
    severity: str  # "critical", "high", "medium", "low"
    enforceable: bool = True


@dataclass
class ValidationResult:
    """Result of validating an action against the constitution."""

    permitted: bool
    violations: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "permitted": self.permitted,
            "violations": self.violations,
            "warnings": self.warnings,
        }


# Immutable constitutional rules
_RULES: list[ConstitutionalRule] = [
    ConstitutionalRule(
        id="C-001",
        name="No Raw Data Sharing",
        description="No user's raw code, keystrokes, or biometric data may leave the local system without explicit consent.",
        violation_type=ViolationType.DATA_EXFILTRATION,
        severity="critical",
    ),
    ConstitutionalRule(
        id="C-002",
        name="Consent Required for Collection",
        description="All sensor data collection (camera, mic, keyboard) requires explicit user opt-in.",
        violation_type=ViolationType.CONSENT_MISSING,
        severity="critical",
    ),
    ConstitutionalRule(
        id="C-003",
        name="Differential Privacy for Skill Diffs",
        description="Any skill pattern shared via P2P must be differentially private (epsilon <= 1.0).",
        violation_type=ViolationType.PRIVACY,
        severity="high",
    ),
    ConstitutionalRule(
        id="C-004",
        name="No Unauthorized System Access",
        description="UCSK agents must not access files, networks, or resources outside the user's declared workspace.",
        violation_type=ViolationType.UNAUTHORIZED_ACCESS,
        severity="critical",
    ),
    ConstitutionalRule(
        id="C-005",
        name="No Harmful Code Generation",
        description="The system must refuse to generate malware, exploits, or code that intentionally harms systems or users.",
        violation_type=ViolationType.HARMFUL_ACTION,
        severity="critical",
    ),
    ConstitutionalRule(
        id="C-006",
        name="Bias Mitigation in Benchmarks",
        description="Performance comparisons must not discriminate based on geography, gender, or identity.",
        violation_type=ViolationType.BIAS_DETECTED,
        severity="high",
    ),
    ConstitutionalRule(
        id="C-007",
        name="User Data Sovereignty",
        description="Users can export or delete all their data at any time. The system must honor deletion requests completely.",
        violation_type=ViolationType.PRIVACY,
        severity="critical",
    ),
    ConstitutionalRule(
        id="C-008",
        name="Transparent Decision Logging",
        description="All autonomous agent decisions must be logged in the audit trail with reasoning.",
        violation_type=ViolationType.UNAUTHORIZED_ACCESS,
        severity="medium",
    ),
]


class Constitution:
    """Enforces UCSK's ethical constitution on all system actions."""

    def __init__(self) -> None:
        self._rules = {r.id: r for r in _RULES}

    @property
    def rules(self) -> list[ConstitutionalRule]:
        return list(self._rules.values())

    def validate_action(self, action: dict[str, Any]) -> ValidationResult:
        """Validate a proposed action against constitutional rules.

        Args:
            action: Dictionary describing the proposed action:
                - type: Action type (e.g., "data_share", "file_access", "code_gen")
                - target: What/who is affected
                - consent: Whether user consent was obtained
                - scope: What data/resources are involved

        Returns:
            ValidationResult indicating whether the action is permitted.
        """
        violations: list[str] = []
        warnings: list[str] = []
        action_type = action.get("type", "")
        has_consent = action.get("consent", False)
        scope = action.get("scope", "")

        # Check data sharing without consent
        if action_type == "data_share" and not has_consent:
            violations.append(f"C-001: Raw data sharing requires explicit consent")

        # Check sensor activation without consent
        if action_type == "sensor_activate" and not has_consent:
            violations.append(f"C-002: Sensor activation requires user opt-in")

        # Check file access scope
        if action_type == "file_access" and scope == "external":
            violations.append(f"C-004: Cannot access resources outside declared workspace")

        # Check harmful code generation
        if action_type == "code_gen":
            intent = action.get("intent", "")
            if intent in ("exploit", "malware", "ddos", "phishing"):
                violations.append(f"C-005: Harmful code generation is prohibited")

        # Warn on actions without audit trail
        if not action.get("logged", True):
            warnings.append("C-008: Action should be logged in audit trail")

        permitted = len(violations) == 0
        if not permitted:
            log.warning(
                "constitution.violation",
                action_type=action_type,
                violations=violations,
            )

        return ValidationResult(
            permitted=permitted,
            violations=violations,
            warnings=warnings,
        )
