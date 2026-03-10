package com.bank.paymentservice.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PaymentServiceService {

    /**
     * Core business logic extracted from monolith.
     * All mutations are wrapped in @Transactional (ACID guarantee).
     */
    @Transactional
    public void process(/* domain params */) {
        // TODO: implement — derived from bounded-context analysis
    }
}