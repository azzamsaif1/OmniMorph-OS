"""Security operations API routes — exposes C-based security agents."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/security", tags=["security"])


class ScanRequest(BaseModel):
    target_ip: str
    scan_type: str = "common"  # common | range
    start_port: int = 1
    end_port: int = 1024


class VulnAnalysisRequest(BaseModel):
    service: str
    banner: str = ""
    port: int


class ExploitSimRequest(BaseModel):
    cve_id: str
    target_ip: str
    target_port: int


class FullAssessmentRequest(BaseModel):
    target_ip: str


@router.post("/scan")
async def scan_target(req: ScanRequest):
    """Scan target for open ports using C-based scanner."""
    try:
        from backend.agents.security.recon_agent import scan_common_ports, scan_port_range
        if req.scan_type == "common":
            result = scan_common_ports(req.target_ip)
        else:
            result = scan_port_range(req.target_ip, req.start_port, req.end_port)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan error: {e}")


@router.post("/vulnerabilities")
async def analyze_vulnerabilities(req: VulnAnalysisRequest):
    """Analyze a service for known CVEs."""
    try:
        from backend.agents.security.vuln_analyzer import analyze_service
        return analyze_service(req.service, req.banner, req.port)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {e}")


@router.post("/exploit/simulate")
async def simulate_exploit(req: ExploitSimRequest):
    """Simulate exploit execution (safe mode — no actual exploitation)."""
    try:
        from backend.agents.security.exploit_agent import simulate_exploit
        return simulate_exploit(req.cve_id, req.target_ip, req.target_port)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {e}")


@router.post("/assessment")
async def full_assessment(req: FullAssessmentRequest):
    """Run full security assessment pipeline: Recon → Analyze → Exploit → Report."""
    try:
        from backend.agents.security.security_orchestrator import SecurityOrchestrator
        orchestrator = SecurityOrchestrator()
        result = await orchestrator.run_full_assessment(req.target_ip)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment error: {e}")
