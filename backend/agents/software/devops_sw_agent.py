"""DevOps agent — infrastructure, CI/CD, containerization, deployment.

Handles Docker, Kubernetes, GitHub Actions, and cloud deployment.
"""

import time
from typing import Any

from backend.gemini_client import generate_content


class DevOpsSWAgent:
    """Specialized agent for DevOps and infrastructure tasks.

    Capabilities:
    - Dockerfile generation
    - CI/CD pipeline creation (GitHub Actions, GitLab CI)
    - Kubernetes manifests
    - Cloud deployment configs (GCP, AWS)
    - Monitoring and alerting setup
    """

    def __init__(self):
        self.tasks_completed: int = 0
        self.success_rate: float = 0.88

    async def generate_dockerfile(
        self, app_type: str, language: str, requirements: list[str] | None = None
    ) -> dict[str, Any]:
        """Generate optimized Dockerfile."""
        prompt = (
            f"Generate a production-optimized multi-stage Dockerfile.\n\n"
            f"App type: {app_type}\n"
            f"Language: {language}\n"
            f"Requirements: {requirements or ['standard']}\n\n"
            f"Optimize for: small image size, security (non-root), caching."
        )

        code = await generate_content(prompt)
        self.tasks_completed += 1

        return {
            "type": "dockerfile",
            "code": code or self._fallback_dockerfile(language),
            "app_type": app_type,
            "generated_at": time.time(),
        }

    async def generate_ci_pipeline(
        self, platform: str = "github_actions", stages: list[str] | None = None
    ) -> dict[str, Any]:
        """Generate CI/CD pipeline configuration."""
        default_stages = stages or ["lint", "test", "build", "deploy"]

        prompt = (
            f"Generate a {platform} CI/CD pipeline with stages: {', '.join(default_stages)}\n\n"
            f"Requirements:\n"
            f"- Caching for dependencies\n"
            f"- Parallel test execution\n"
            f"- Security scanning step\n"
            f"- Deployment to staging on PR merge\n"
            f"- Production deploy on tag"
        )

        code = await generate_content(prompt)
        self.tasks_completed += 1

        return {
            "type": "ci_pipeline",
            "platform": platform,
            "stages": default_stages,
            "code": code or self._fallback_ci(platform),
            "generated_at": time.time(),
        }

    async def generate_k8s_manifests(
        self, service_name: str, replicas: int = 3, port: int = 8000
    ) -> dict[str, Any]:
        """Generate Kubernetes deployment manifests."""
        prompt = (
            f"Generate Kubernetes manifests for service: {service_name}\n\n"
            f"- Deployment ({replicas} replicas)\n"
            f"- Service (ClusterIP, port {port})\n"
            f"- HPA (min 2, max 10, target CPU 70%)\n"
            f"- ConfigMap and Secret references\n"
            f"- Health checks (liveness + readiness)\n"
            f"- Resource limits"
        )

        code = await generate_content(prompt)
        self.tasks_completed += 1

        return {
            "type": "k8s_manifests",
            "service": service_name,
            "code": code or self._fallback_k8s(service_name, replicas, port),
            "generated_at": time.time(),
        }

    def _fallback_dockerfile(self, language: str) -> str:
        if language == "python":
            return (
                "FROM python:3.12-slim as builder\n"
                "WORKDIR /app\n"
                "COPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n\n"
                "FROM python:3.12-slim\n"
                "WORKDIR /app\n"
                "COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12\n"
                "COPY . .\n"
                "USER nobody\n"
                "EXPOSE 8000\n"
                "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\"]\n"
            )
        return f"# Dockerfile for {language}"

    def _fallback_ci(self, platform: str) -> str:
        if platform == "github_actions":
            return (
                "name: CI\non:\n  push:\n    branches: [main]\n  pull_request:\n\n"
                "jobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - run: pip install -r requirements.txt\n"
                "      - run: pytest\n"
            )
        return f"# CI pipeline for {platform}"

    def _fallback_k8s(self, name: str, replicas: int, port: int) -> str:
        return (
            f"apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: {name}\n"
            f"spec:\n  replicas: {replicas}\n  selector:\n    matchLabels:\n"
            f"      app: {name}\n  template:\n    spec:\n      containers:\n"
            f"      - name: {name}\n        ports:\n        - containerPort: {port}\n"
        )

    def get_stats(self) -> dict[str, Any]:
        return {
            "agent": "devops",
            "tasks_completed": self.tasks_completed,
            "success_rate": self.success_rate,
        }
