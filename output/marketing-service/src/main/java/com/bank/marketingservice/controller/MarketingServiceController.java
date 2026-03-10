package com.bank.marketingservice.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.bank.marketingservice.service.MarketingServiceService;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/marketings")
@RequiredArgsConstructor
public class MarketingServiceController {

    private final MarketingServiceService service;

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("UP");
    }

    // TODO: Add domain-specific endpoints derived from bounded context
}