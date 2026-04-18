package com.job_recommender_system.auth_server.controllers;

import com.job_recommender_system.auth_server.dto.StripePaymentRequest;
import com.job_recommender_system.auth_server.services.StripePaymentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/payments")
@RequiredArgsConstructor
public class GeneralPaymentController {
    private final StripePaymentService stripePaymentService;

    @PostMapping("/create-checkout-session")
    public ResponseEntity<Map> createCheckoutSession(@RequestBody StripePaymentRequest request, Authentication authentication) throws Exception {
        String url = stripePaymentService.createPayment(request, authentication);
        return ResponseEntity.ok(Map.of(
                "checkoutUrl", url
        ));
    }
}
