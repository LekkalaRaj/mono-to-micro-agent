package com.bank.productservice.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.bank.productservice.service.ProductServiceService;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductServiceController {

    private final ProductServiceService service;

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("UP");
    }

    // TODO: Add domain-specific endpoints derived from bounded context
}