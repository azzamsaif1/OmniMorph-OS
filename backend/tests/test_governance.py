"""Tests for governance API — constitution, privacy budget, audit trail."""

from __future__ import annotations

import pytest

from backend.governance.constitution import Constitution, ViolationType


class TestConstitution:
    def setup_method(self):
        self.constitution = Constitution()

    def test_has_eight_rules(self):
        assert len(self.constitution.rules) == 8

    def test_first_rule_is_no_raw_data_sharing(self):
        rules = self.constitution.rules
        assert rules[0].id == "C-001"
        assert rules[0].name == "No Raw Data Sharing"
        assert rules[0].severity == "critical"

    def test_validate_permitted_action(self):
        result = self.constitution.validate_action({
            "type": "code_gen",
            "consent": True,
            "scope": "internal",
        })
        assert result.permitted is True
        assert result.violations == []

    def test_data_share_without_consent_blocked(self):
        result = self.constitution.validate_action({
            "type": "data_share",
            "consent": False,
        })
        assert result.permitted is False
        assert len(result.violations) == 1
        assert "C-001" in result.violations[0]

    def test_sensor_activate_without_consent_blocked(self):
        result = self.constitution.validate_action({
            "type": "sensor_activate",
            "consent": False,
        })
        assert result.permitted is False
        assert "C-002" in result.violations[0]

    def test_external_file_access_blocked(self):
        result = self.constitution.validate_action({
            "type": "file_access",
            "scope": "external",
        })
        assert result.permitted is False
        assert "C-004" in result.violations[0]

    def test_harmful_code_gen_blocked(self):
        result = self.constitution.validate_action({
            "type": "code_gen",
            "intent": "malware",
        })
        assert result.permitted is False
        assert "C-005" in result.violations[0]

    def test_unlogged_action_generates_warning(self):
        result = self.constitution.validate_action({
            "type": "code_gen",
            "logged": False,
        })
        assert result.permitted is True
        assert len(result.warnings) == 1
        assert "C-008" in result.warnings[0]

    def test_validation_result_to_dict(self):
        result = self.constitution.validate_action({"type": "code_gen"})
        d = result.to_dict()
        assert "permitted" in d
        assert "violations" in d
        assert "warnings" in d


@pytest.mark.anyio
async def test_get_constitution_api(client):
    resp = await client.get("/api/governance/constitution")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_rules"] == 8
    rules = data["rules"]
    assert rules[0]["name"] == "No Raw Data Sharing"
    assert rules[0]["severity"] == "critical"


@pytest.mark.anyio
async def test_validate_action_api_permitted(client):
    resp = await client.post(
        "/api/governance/constitution/validate",
        json={"type": "code_gen", "consent": True, "scope": "internal"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["permitted"] is True
    assert data["violations"] == []


@pytest.mark.anyio
async def test_validate_action_api_denied(client):
    resp = await client.post(
        "/api/governance/constitution/validate",
        json={"type": "data_share", "consent": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["permitted"] is False
    assert len(data["violations"]) >= 1


@pytest.mark.anyio
async def test_privacy_budget_api(client):
    resp = await client.get("/api/governance/privacy/budget/default")
    assert resp.status_code == 200
    data = resp.json()
    assert data["epsilon_total"] == 1.0
    assert data["epsilon_remaining"] == 1.0
    assert data["exhausted"] is False


@pytest.mark.anyio
async def test_audit_trail_api(client):
    resp = await client.get("/api/governance/audit")
    assert resp.status_code == 200
    data = resp.json()
    assert "entries" in data
    assert "total" in data
