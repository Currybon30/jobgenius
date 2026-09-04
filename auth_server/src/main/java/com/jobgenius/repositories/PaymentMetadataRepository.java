package com.jobgenius.repositories;

import java.util.Optional;

import com.jobgenius.models.PaymentMetadata;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PaymentMetadataRepository extends JpaRepository<PaymentMetadata, Long> {
    Optional<PaymentMetadata> findByPayment_PaymentId(Long paymentId);

    PaymentMetadata findByKeyAndValue(String key, String value);
}
