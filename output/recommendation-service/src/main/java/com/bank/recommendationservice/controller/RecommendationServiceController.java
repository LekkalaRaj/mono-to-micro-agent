package com.bank.recommendationservice.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.bank.recommendationservice.service.RecommendationServiceService;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/recommendations")
@RequiredArgsConstructor
public class RecommendationServiceController {

    private final RecommendationServiceService service;

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("UP");
    }

    // TODO: Add domain-specific endpoints derived from bounded context
}