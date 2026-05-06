package com.job_recommender_system.auth_server.repositories;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.job_recommender_system.auth_server.models.Payment;

public interface PaymentRepository extends JpaRepository<Payment, Long> {
    Optional<Payment> findByProviderPaymentRef(String providerPaymentRef);

    Optional<List<Payment>> findByUser_Uid(Long uid);

    Optional<List<Payment>> findByUser_UidAndStatus(Long uid, String status);

}
