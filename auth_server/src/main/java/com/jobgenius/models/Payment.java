package com.jobgenius.models;

import java.time.OffsetDateTime;

import com.jobgenius.utils.PaymentStatus;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.ForeignKey;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "payments", indexes = {
        @Index(name = "idx_payment_user_id", columnList = "uid")
})
@Getter
@Setter
public class Payment {
        @Id
        @GeneratedValue(strategy = GenerationType.IDENTITY)
        private Long paymentId;

        @ManyToOne
        @JoinColumn(name = "uid", nullable = false, foreignKey = @ForeignKey(name = "fk_payment_user"))
        private User user;

        @Column(nullable = false)
        @Enumerated(EnumType.STRING)
        private PaymentStatus status; // "PENDING", "PAID", "FAILED"

        @Column(nullable = false)
        private String provider;

        @Column(nullable = false)
        private String providerPaymentRef;

        @Column(nullable = false)
        private OffsetDateTime createdAt;

        @Column(nullable = false)
        private OffsetDateTime updatedAt;
}