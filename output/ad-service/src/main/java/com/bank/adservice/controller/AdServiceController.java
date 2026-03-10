package com.bank.adservice.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.bank.adservice.service.AdServiceService;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/ads")
@RequiredArgsConstructor
public class AdServiceController {

    private final AdServiceService service;

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("UP");
    }

    // TODO: Add domain-specific endpoints derived from bounded context
}