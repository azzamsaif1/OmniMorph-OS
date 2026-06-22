"""Docker agent — container build, deployment, and management.

Target: 99% uptime for deployed containers.
"""

import subprocess
import time
from typing import Any

from backend.gemini_client import generate_content


class DockerAgent:
    """Automated container management agent.

    Capabilities:
    - Dockerfile generation/optimization
    - Image building
    - Container deployment
    - Health monitoring
    - Multi-container orchestration
    """

    def __init__(self):
        self.deployments: int = 0
        self.builds: int = 0

    async def build_image(
        self, image_name: str, dockerfile_path: str = ".", tag: str = "latest"
    ) -> dict[str, Any]:
        """Build a Docker image."""
        full_tag = f"{image_name}:{tag}"

        try:
            result = subprocess.run(
                ["docker", "build", "-t", full_tag, dockerfile_path],
                capture_output=True, text=True, timeout=300
            )
            self.builds += 1

            return {
                "image": full_tag,
                "success": result.returncode == 0,
                "output": result.stdout[-500:] if result.returncode == 0 else result.stderr[-500:],
                "built_at": time.time(),
            }
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"image": full_tag, "success": False, "error": str(e)}

    async def deploy_container(
        self, image: str, port_mapping: str = "8000:8000",
        env_vars: dict | None = None, name: str | None = None
    ) -> dict[str, Any]:
        """Deploy a container from an image."""
        cmd = ["docker", "run", "-d", "-p", port_mapping]

        if name:
            cmd.extend(["--name", name])
        if env_vars:
            for key, value in env_vars.items():
                cmd.extend(["-e", f"{key}={value}"])
        cmd.append(image)

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
            self.deployments += 1

            container_id = result.stdout.strip()[:12] if result.returncode == 0 else None

            return {
                "image": image,
                "container_id": container_id,
                "success": result.returncode == 0,
                "port_mapping": port_mapping,
                "deployed_at": time.time(),
            }
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"image": image, "success": False, "error": str(e)}

    def list_containers(self, all_containers: bool = False) -> dict[str, Any]:
        """List running containers."""
        cmd = ["docker", "ps", "--format", "{{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"]
        if all_containers:
            cmd.append("-a")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            containers = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        containers.append({
                            "id": parts[0],
                            "image": parts[1],
                            "status": parts[2],
                            "ports": parts[3] if len(parts) > 3 else "",
                        })
            return {"containers": containers, "count": len(containers)}
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"error": str(e), "containers": []}

    async def health_check(self, container_id: str) -> dict[str, Any]:
        """Check container health."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_id],
                capture_output=True, text=True, timeout=10
            )
            status = result.stdout.strip()

            return {
                "container_id": container_id,
                "healthy": status == "healthy" or "running" in status.lower(),
                "status": status or "unknown",
                "checked_at": time.time(),
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"container_id": container_id, "healthy": False, "status": "unreachable"}

    async def generate_compose(self, services: list[dict]) -> dict[str, Any]:
        """Generate docker-compose.yml from service descriptions."""
        prompt = (
            f"Generate docker-compose.yml for these services:\n\n"
            + "\n".join(f"- {s.get('name', 'service')}: {s.get('description', '')}" for s in services)
            + "\n\nInclude: healthchecks, volumes, networks, resource limits."
        )

        compose = await generate_content(prompt)

        return {
            "type": "docker_compose",
            "services": [s.get("name") for s in services],
            "content": compose or self._fallback_compose(services),
            "generated_at": time.time(),
        }

    def _fallback_compose(self, services: list[dict]) -> str:
        lines = ["version: '3.8'\nservices:"]
        for svc in services:
            name = svc.get("name", "service")
            lines.append(f"  {name}:")
            lines.append(f"    build: .")
            lines.append(f"    ports:")
            lines.append(f"      - '{svc.get('port', 8000)}:{svc.get('port', 8000)}'")
        return "\n".join(lines)

    def get_stats(self) -> dict[str, Any]:
        return {
            "agent": "docker",
            "builds": self.builds,
            "deployments": self.deployments,
        }
