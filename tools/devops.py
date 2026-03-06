"""
tools/devops.py
────────────────
Tool 4 — DevOps
Generates production-ready Dockerfile, Helm chart, and Kubernetes manifests
for a single microservice.

K8s template rendering is delegated to utils/k8s_codegen.py.
Settings (registry, OTEL endpoint) are injected via config.get_settings().
"""

from __future__ import annotations

from config.settings import get_settings
from models.schemas import DevOpsInput, DevOpsOutput
from utils.logger import get_logger
from utils.k8s_codegen  import (
    render_dockerfile, render_deployment, render_service,
    render_ingress, render_configmap, render_secrets,
    render_hpa, render_helm_chart,
)

logger   = get_logger(__name__)
settings = get_settings()


def devops_tool(service_name: str, replicas: int = 2, port: int = 8080) -> dict:
    """
    Generate Dockerfile, Helm chart, and Kubernetes manifests.

    Args:
        service_name: e.g. "payment-service"
        replicas:     Baseline pod replica count
        port:         Container HTTP port

    Returns:
        Serialised DevOpsOutput as a plain dict (ADK requirement).
    """
    _input = DevOpsInput(service_name=service_name, replicas=replicas, port=port)
    svc    = _input.service_name
    path_prefix = svc.split("-")[0]

    logger.info("Generating infra artefacts for service: %s  replicas=%d  port=%d", svc, replicas, port)

    output = DevOpsOutput(
        service_name=svc,
        dockerfile=render_dockerfile(svc, port, settings.container_registry),
        helm_chart_yaml=render_helm_chart(svc),
        deployment_yaml=render_deployment(svc, replicas, port, settings.container_registry),
        service_yaml=render_service(svc, port),
        ingress_yaml=render_ingress(svc, path_prefix),
        configmap_yaml=render_configmap(svc, port, settings.otel_collector_endpoint),
        secrets_yaml=render_secrets(svc),
        hpa_yaml=render_hpa(svc, min_replicas=replicas, max_replicas=replicas * 5),
    )

    import os
    k8s_dir = os.path.join("output", svc, "k8s")
    os.makedirs(k8s_dir, exist_ok=True)
    
    with open(os.path.join("output", svc, "Dockerfile"), "w", encoding="utf-8") as f:
        f.write(output.dockerfile)
        
    with open(os.path.join(k8s_dir, "Chart.yaml"), "w", encoding="utf-8") as f:
        f.write(output.helm_chart_yaml)
    with open(os.path.join(k8s_dir, "deployment.yaml"), "w", encoding="utf-8") as f:
        f.write(output.deployment_yaml)
    with open(os.path.join(k8s_dir, "service.yaml"), "w", encoding="utf-8") as f:
        f.write(output.service_yaml)
    with open(os.path.join(k8s_dir, "ingress.yaml"), "w", encoding="utf-8") as f:
        f.write(output.ingress_yaml)
    with open(os.path.join(k8s_dir, "configmap.yaml"), "w", encoding="utf-8") as f:
        f.write(output.configmap_yaml)
    with open(os.path.join(k8s_dir, "secrets.yaml"), "w", encoding="utf-8") as f:
        f.write(output.secrets_yaml)
    with open(os.path.join(k8s_dir, "hpa.yaml"), "w", encoding="utf-8") as f:
        f.write(output.hpa_yaml)

    logger.info("DevOps artefacts generated for: %s", svc)
    return output.model_dump()