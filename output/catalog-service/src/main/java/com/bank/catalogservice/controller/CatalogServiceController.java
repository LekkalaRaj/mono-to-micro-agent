package com.bank.catalogservice.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.bank.catalogservice.service.CatalogServiceService;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/catalogs")
@RequiredArgsConstructor
public class CatalogServiceController {

    private final CatalogServiceService service;

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("UP");
    }

    // TODO: Add domain-specific endpoints derived from bounded context
}