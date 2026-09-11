package com.jobgenius.controllers;

import com.jobgenius.dto.StripePaymentRequest;
import com.jobgenius.repositories.UserRepository;
import com.jobgenius.repositories.PaymentMetadataRepository;
import com.jobgenius.services.StripePaymentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/payments")
@RequiredArgsConstructor
public class GeneralPaymentController {
    private final StripePaymentService stripePaymentService;
    private final UserRepository userRepository;
    private final PaymentMetadataRepository paymentMetadataRepository;

    @PostMapping("/create-checkout-session")
    public ResponseEntity<Map> createCheckoutSession(@RequestBody StripePaymentRequest request,
            Authentication authentication) throws Exception {
        String url = stripePaymentService.createPayment(request, authentication);
        return ResponseEntity.ok(Map.of(
                "checkoutUrl", url));
    }

    @PostMapping("/cancel-subscription")
    public ResponseEntity<Map> cancelSubscription(Authentication authentication) throws Exception {
        Long userId = userRepository.findByEmail(authentication.getName())
                .orElseThrow(() -> new RuntimeException("User not found"))
                .getUid();

        String subscriptionId = paymentMetadataRepository.findLatestSubscriptionIdByUserId(userId)
                .orElseThrow(() -> new RuntimeException("Subscription not found"));

        String message = stripePaymentService.cancelSubscription(subscriptionId);
        return ResponseEntity.ok(Map.of(
                "message", message));
    }
}
