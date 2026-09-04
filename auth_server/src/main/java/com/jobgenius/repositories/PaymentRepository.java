package com.jobgenius.repositories;

import java.util.List;
import java.util.Optional;

import com.jobgenius.models.Payment;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PaymentRepository extends JpaRepository<Payment, Long> {
    Optional<Payment> findByProviderPaymentRef(String providerPaymentRef);

    List<Payment> findByUser_Uid(Long uid);

    List<Payment> findByUser_UidAndStatus(Long uid, String status);

}
