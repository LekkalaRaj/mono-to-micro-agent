"""
utils/k8s_codegen.py
─────────────────────
Pure-Python helpers that render Kubernetes YAML and Helm chart files.
Each function is independently unit-testable and has a single responsibility.
To add a new manifest type (e.g., NetworkPolicy, PodDisruptionBudget),
add a function here and call it from devops_tool.py.
"""

from __future__ import annotations

import textwrap


def render_dockerfile(svc: str, port: int, registry: str) -> str:
    return textwrap.dedent(f"""
        # ── Stage 1: Build ────────────────────────────────────────────────
        FROM eclipse-temurin:21-jdk-alpine AS builder
        WORKDIR /app
        COPY pom.xml .
        COPY src ./src
        RUN ./mvnw -q package -DskipTests

        # ── Stage 2: Distroless runtime (minimal attack surface) ─────────
        FROM gcr.io/distroless/java21-debian12
        LABEL maintainer="platform-engineering@bank.internal"
        LABEL org.opencontainers.image.title="{svc}"
        LABEL org.opencontainers.image.source="https://github.com/bank/{svc}"

        WORKDIR /app
        COPY --from=builder /app/target/*.jar app.jar

        EXPOSE {port}
        ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
    """).strip()


def render_deployment(svc: str, replicas: int, port: int, registry: str) -> str:
    return textwrap.dedent(f"""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: {svc}
          labels:
            app: {svc}
            version: "1.0.0"
        spec:
          replicas: {replicas}
          selector:
            matchLabels:
              app: {svc}
          template:
            metadata:
              labels:
                app: {svc}
              annotations:
                prometheus.io/scrape: "true"
                prometheus.io/path:   "/actuator/prometheus"
                prometheus.io/port:   "{port}"
            spec:
              serviceAccountName: {svc}-sa
              securityContext:
                runAsNonRoot: true
                runAsUser:    10001
                fsGroup:      10001
              containers:
                - name:  {svc}
                  image: {registry}/{svc}:${{IMAGE_TAG}}
                  ports:
                    - containerPort: {port}
                  envFrom:
                    - configMapRef:
                        name: {svc}-config
                    - secretRef:
                        name: {svc}-secrets
                  resources:
                    requests: {{ cpu: "250m",  memory: "512Mi" }}
                    limits:   {{ cpu: "1000m", memory: "1Gi"   }}
                  livenessProbe:
                    httpGet:
                      path: /actuator/health/liveness
                      port: {port}
                    initialDelaySeconds: 30
                    periodSeconds:       10
                    failureThreshold:     3
                  readinessProbe:
                    httpGet:
                      path: /actuator/health/readiness
                      port: {port}
                    initialDelaySeconds: 20
                    periodSeconds:        5
                  volumeMounts:
                    - name: tmp
                      mountPath: /tmp
              volumes:
                - name: tmp
                  emptyDir: {{}}
    """).strip()


def render_service(svc: str, port: int) -> str:
    return textwrap.dedent(f"""
        apiVersion: v1
        kind: Service
        metadata:
          name: {svc}
          labels:
            app: {svc}
        spec:
          selector:
            app: {svc}
          ports:
            - protocol: TCP
              port:       80
              targetPort: {port}
          type: ClusterIP
    """).strip()


def render_ingress(svc: str, path_prefix: str) -> str:
    return textwrap.dedent(f"""
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        metadata:
          name: {svc}-ingress
          annotations:
            nginx.ingress.kubernetes.io/rewrite-target: /
            nginx.ingress.kubernetes.io/ssl-redirect:   "true"
        spec:
          ingressClassName: nginx
          tls:
            - hosts:
                - api.bank.internal
              secretName: bank-tls
          rules:
            - host: api.bank.internal
              http:
                paths:
                  - path:     /api/{path_prefix}s
                    pathType: Prefix
                    backend:
                      service:
                        name: {svc}
                        port:
                          number: 80
    """).strip()


def render_configmap(svc: str, port: int, otel_endpoint: str) -> str:
    return textwrap.dedent(f"""
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: {svc}-config
        data:
          SPRING_PROFILES_ACTIVE:                    "prod"
          SERVER_PORT:                               "{port}"
          MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE: "health,info,prometheus"
          OTEL_SERVICE_NAME:                         "{svc}"
          OTEL_EXPORTER_OTLP_ENDPOINT:               "{otel_endpoint}"
    """).strip()


def render_secrets(svc: str) -> str:
    return textwrap.dedent(f"""
        # ⚠️  PLACEHOLDER ONLY — inject real values via HashiCorp Vault / ESO.
        # Never commit plaintext credentials.
        apiVersion: v1
        kind: Secret
        metadata:
          name: {svc}-secrets
          annotations:
            vault.hashicorp.com/agent-inject:              "true"
            vault.hashicorp.com/role:                      "{svc}"
            vault.hashicorp.com/agent-inject-secret-db:    "secret/data/{svc}/db"
        type: Opaque
        # stringData populated at runtime by Vault sidecar
    """).strip()


def render_hpa(svc: str, min_replicas: int, max_replicas: int) -> str:
    return textwrap.dedent(f"""
        apiVersion: autoscaling/v2
        kind: HorizontalPodAutoscaler
        metadata:
          name: {svc}-hpa
        spec:
          scaleTargetRef:
            apiVersion: apps/v1
            kind:        Deployment
            name:        {svc}
          minReplicas: {min_replicas}
          maxReplicas: {max_replicas}
          metrics:
            - type: Resource
              resource:
                name: cpu
                target:
                  type:               Utilization
                  averageUtilization: 65
            - type: Resource
              resource:
                name: memory
                target:
                  type:               Utilization
                  averageUtilization: 80
    """).strip()


def render_helm_chart(svc: str) -> str:
    return textwrap.dedent(f"""
        apiVersion: v2
        name:        {svc}
        description: Helm chart for {svc} microservice
        type:        application
        version:     0.1.0
        appVersion:  "1.0.0"
        keywords:
          - banking
          - microservice
          - strangler-fig
        maintainers:
          - name:  Platform Engineering
            email: platform-engineering@bank.internal
    """).strip()