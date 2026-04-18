package com.job_recommender_system.auth_server.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class StripePaymentRequest {
    private String successUrl;
    private String cancelUrl;
}
