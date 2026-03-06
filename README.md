# 🏗️ MonoToMicro (M2M) Agent

> **"Bridging Legacy with Agentic AI."**

The **MonoToMicro (M2M) Agent** is an enterprise-grade AI orchestrator built on the **Google Agent Development Kit (ADK)**. It is specifically designed to automate the complex, high-risk journey of migrating legacy Java monolithic applications to modern, cloud-native microservices within highly regulated financial environments.

---

## 🏛️ Project Vision
In a old financial institution, code isn't just software; it's history. The M2M Agent respects this legacy by providing a "Zero-Defect" migration path. It autonomously analyzes, documents, refactors, and secures mission-critical logic, transforming "Black Box" monoliths into agile, observable microservices.

---

## 🚀 Key Features

### 1. Intelligent Discovery & Visualization
* **Deep Repository Analysis:** Scans entire GitHub codebases to identify Bounded Contexts using Domain-Driven Design (DDD).
* **Automated Documentation:** Generates comprehensive Markdown-based documentation for existing logic.
* **Architectural Mapping:** Produces High-Level (HLD) and Low-Level (LLD) diagrams using Mermaid.js.



### 2. Autonomous Decomposition & Refactoring
* **Strangler Fig Implementation:** Proposes an incremental migration strategy to ensure zero downtime.
* **Pattern-Based Refactoring:** Automatically suggests and implements patterns like **Saga**, **API Gateway**, and **Database-per-Service**.
* **Traffic Routing Blueprint:** Generates configuration for NGINX, Istio, or Cloud Ingress to manage the transition from monolith to microservices.



### 3. Full-Spectrum Test Engineering
The M2M Agent guarantees stability by generating a robust testing pyramid:
* **Unit & Component Testing:** JUnit 5 and Mockito coverage for all extracted methods.
* **Integration Testing:** Validation of database persistence and external API calls.
* **Contractual Testing:** Implementation of Pact or Spring Cloud Contract to maintain service-to-service integrity.
* **Edge Case Intelligence:** AI-driven analysis of financial boundary conditions, null-handling, and exception flows.



### 4. Production-Ready DevOps
* **Secured Containerization:** Generates multi-stage, distroless `Dockerfiles` optimized for Java 17/21.
* **Kubernetes Orchestration:** Provides full **Helm Charts** including Deployments, HPA, Services, and ConfigMaps.
* **Observability-by-Design:** Pre-configures health checks (Liveness/Readiness) and Prometheus metrics.

---

## 🛠️ Technical Stack
* **Orchestration:** [Google Agent Development Kit (ADK)](https://github.com/google/braid-adk)
* **Core Logic:** Python / Java
* **LLM Foundations:** Gemini 1.5 Pro (via Vertex AI)
* **Legacy Frameworks:** Spring Legacy, EJB, Plain Java
* **Target Frameworks:** Spring Boot 3.x, Spring Cloud
* **Infrastructure:** Kubernetes (GKE/On-Prem), Docker, Helm, Istio

---

## 📋 How It Works (Agentic Workflow)

1.  **Ingestion:** Point the M2M Agent at a GitHub URL.
2.  **The Analysis Agent:** Maps dependencies, identifies "God Classes," and builds the Domain Map.
3.  **The Architect Agent:** Proposes the microservice boundaries and generates the Mermaid diagrams.
4.  **The Implementation Agent:** Generates the new Spring Boot code, refactoring logic from the monolith.
5.  **The QA Agent:** Writes the full testing suite and validates the refactored code.
6.  **The DevOps Agent:** Outputs the Docker and Helm artifacts for deployment.



---

## 💎 Expected Impact

| Metric | Target |
| :--- | :--- |
| **Migration Velocity** | 60% reduction in manual effort |
| **Test Coverage** | ~100% method-level coverage |
| **Risk Mitigation** | Automated regression and contract validation |
| **Consistency** | Standardized service templates and deployment manifests |

---