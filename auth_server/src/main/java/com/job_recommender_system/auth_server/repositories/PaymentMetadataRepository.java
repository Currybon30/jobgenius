package com.job_recommender_system.auth_server.repositories;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.job_recommender_system.auth_server.models.PaymentMetadata;

public interface PaymentMetadataRepository extends JpaRepository<PaymentMetadata, Long> {
    Optional<PaymentMetadata> findByPayment_PaymentId(Long paymentId);

    PaymentMetadata findByKeyAndValue(String key, String value);
}
