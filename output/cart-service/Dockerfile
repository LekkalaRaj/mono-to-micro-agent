# ── Stage 1: Build ────────────────────────────────────────────────
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN ./mvnw -q package -DskipTests

# ── Stage 2: Distroless runtime (minimal attack surface) ─────────
FROM gcr.io/distroless/java21-debian12
LABEL maintainer="platform-engineering@bank.internal"
LABEL org.opencontainers.image.title="cart-service"
LABEL org.opencontainers.image.source="https://github.com/bank/cart-service"

WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]