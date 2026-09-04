package com.jobgenius.controllers;

import java.util.Map;

import com.jobgenius.dto.StripePaymentRequest;
import com.jobgenius.services.StripePaymentService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/payments")
@RequiredArgsConstructor
public class GeneralPaymentController {
    private final StripePaymentService stripePaymentService;

    @PostMapping("/create-checkout-session")
    public ResponseEntity<Map> createCheckoutSession(@RequestBody StripePaymentRequest request,
            Authentication authentication) throws Exception {
        String url = stripePaymentService.createPayment(request, authentication);
        return ResponseEntity.ok(Map.of(
                "checkoutUrl", url));
    }
}
