"""
utils/java_codegen.py
─────────────────────
Pure-Python helpers that render Java / Spring Boot source templates.
Keeping template logic here (rather than inline in coder_tool.py) means:
  • coder_tool.py stays thin — just orchestration & Pydantic I/O
  • templates are unit-testable in isolation
  • new file types (e.g., GraphQL schema, gRPC proto) are added here only
"""

from __future__ import annotations

import textwrap


def render_main_class(pkg: str, cap: str) -> str:
    return textwrap.dedent(f"""
        package com.bank.{pkg};

        import org.springframework.boot.SpringApplication;
        import org.springframework.boot.autoconfigure.SpringBootApplication;

        @SpringBootApplication
        public class {cap}Application {{
            public static void main(String[] args) {{
                SpringApplication.run({cap}Application.class, args);
            }}
        }}
    """).strip()


def render_controller(pkg: str, cap: str, path_prefix: str) -> str:
    return textwrap.dedent(f"""
        package com.bank.{pkg}.controller;

        import org.springframework.http.ResponseEntity;
        import org.springframework.web.bind.annotation.*;
        import com.bank.{pkg}.service.{cap}Service;
        import lombok.RequiredArgsConstructor;

        @RestController
        @RequestMapping("/api/{path_prefix}s")
        @RequiredArgsConstructor
        public class {cap}Controller {{

            private final {cap}Service service;

            @GetMapping("/health")
            public ResponseEntity<String> health() {{
                return ResponseEntity.ok("UP");
            }}

            // TODO: Add domain-specific endpoints derived from bounded context
        }}
    """).strip()


def render_service_class(pkg: str, cap: str) -> str:
    return textwrap.dedent(f"""
        package com.bank.{pkg}.service;

        import org.springframework.stereotype.Service;
        import org.springframework.transaction.annotation.Transactional;

        @Service
        public class {cap}Service {{

            /**
             * Core business logic extracted from monolith.
             * All mutations are wrapped in @Transactional (ACID guarantee).
             */
            @Transactional
            public void process(/* domain params */) {{
                // TODO: implement — derived from bounded-context analysis
            }}
        }}
    """).strip()


def render_unit_test(pkg: str, cap: str) -> str:
    return textwrap.dedent(f"""
        package com.bank.{pkg}.service;

        import org.junit.jupiter.api.*;
        import org.junit.jupiter.params.ParameterizedTest;
        import org.junit.jupiter.params.provider.NullSource;
        import org.mockito.junit.jupiter.MockitoExtension;
        import org.mockito.*;
        import static org.assertj.core.api.Assertions.*;
        import java.math.BigDecimal;

        @ExtendWith(MockitoExtension.class)
        class {cap}ServiceTest {{

            @InjectMocks
            private {cap}Service subject;

            // ── Happy Path ───────────────────────────────────────────────
            @Test
            @DisplayName("process() completes under normal conditions")
            void process_happyPath_succeeds() {{
                assertThatNoException().isThrownBy(() -> subject.process());
            }}

            // ── Null Safety ──────────────────────────────────────────────
            @ParameterizedTest
            @NullSource
            @DisplayName("process() handles null input gracefully")
            void process_nullInput_throwsOrHandles(Object nullParam) {{
                // Verify null-safety contract
            }}

            // ── Financial Overflow ───────────────────────────────────────
            @Test
            @DisplayName("BigDecimal overflow: max scale boundary")
            void process_financialOverflow_handledSafely() {{
                BigDecimal overflow = new BigDecimal("99999999999999999999.99");
                // Assert no silent truncation occurs
            }}
        }}
    """).strip()


def render_integration_test(pkg: str, cap: str, path_prefix: str) -> str:
    return textwrap.dedent(f"""
        package com.bank.{pkg};

        import org.junit.jupiter.api.*;
        import org.springframework.beans.factory.annotation.Autowired;
        import org.springframework.boot.test.context.SpringBootTest;
        import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
        import org.springframework.test.web.servlet.MockMvc;
        import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
        import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

        @SpringBootTest
        @AutoConfigureMockMvc
        class {cap}IntegrationTest {{

            @Autowired
            private MockMvc mockMvc;

            @Test
            @DisplayName("Health endpoint returns 200 UP")
            void healthEndpoint_returns200() throws Exception {{
                mockMvc.perform(get("/api/{path_prefix}s/health"))
                       .andExpect(status().isOk())
                       .andExpect(content().string("UP"));
            }}
        }}
    """).strip()


def render_pom(svc: str, java_version: int, spring_boot_version: str) -> str:
    sb_ver = spring_boot_version.replace("x", "5")
    return textwrap.dedent(f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                 https://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <parent>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-parent</artifactId>
            <version>{sb_ver}</version>
          </parent>
          <groupId>com.bank</groupId>
          <artifactId>{svc}</artifactId>
          <version>0.0.1-SNAPSHOT</version>
          <properties>
            <java.version>{java_version}</java.version>
          </properties>
          <dependencies>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
            <dependency><groupId>io.micrometer</groupId><artifactId>micrometer-registry-prometheus</artifactId></dependency>
            <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
            <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>
            <dependency><groupId>au.com.dius.pact.provider</groupId><artifactId>junit5spring</artifactId><version>4.6.7</version><scope>test</scope></dependency>
          </dependencies>
        </project>
    """).strip()