package com.job_recommender_system.auth_server.repositories;

import com.job_recommender_system.auth_server.models.PaymentMetadata;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface PaymentMetadataRepository extends JpaRepository<PaymentMetadata, Long> {
    Optional<PaymentMetadata> findByPayment_PaymentId(Long paymentId);

    PaymentMetadata findByKeyAndValue(String key, String value);
}
