package com.job_recommender_system.auth_server.controllers;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.job_recommender_system.auth_server.services.StripePaymentService;
import com.stripe.exception.EventDataObjectDeserializationException;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/stripe")
@RequiredArgsConstructor
public class StripePaymentController {
    private final StripePaymentService stripePaymentService;
    @PostMapping("/webhook")
    public ResponseEntity<String> handleWebhook(
            @RequestBody String payload,
            @RequestHeader("Stripe-Signature") String signature) throws JsonProcessingException, EventDataObjectDeserializationException {

        stripePaymentService.handleWebhook(payload, signature);

        return ResponseEntity.ok("ok");
    }
}
