package com.jobgenius.controllers;

import com.jobgenius.services.StripePaymentService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.stripe.exception.EventDataObjectDeserializationException;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/stripe")
@RequiredArgsConstructor
public class StripePaymentController {
    private final StripePaymentService stripePaymentService;

    @PostMapping("/webhook")
    public ResponseEntity<String> handleWebhook(
            @RequestBody String payload,
            @RequestHeader("Stripe-Signature") String signature)
            throws JsonProcessingException, EventDataObjectDeserializationException {

        stripePaymentService.handleWebhook(payload, signature);

        return ResponseEntity.ok("ok");
    }
}
