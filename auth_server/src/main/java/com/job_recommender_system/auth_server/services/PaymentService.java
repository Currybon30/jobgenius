package com.job_recommender_system.auth_server.services;

import org.springframework.security.core.Authentication;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
public abstract class PaymentService {
    public abstract String createPayment(Object request, Authentication authentication) throws Exception;

    public abstract String cancelSubscription(String subscriptionId) throws Exception;

    public abstract void handleWebhook(String payload, String sigHeader) throws Exception;
}
