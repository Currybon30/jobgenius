package com.job_recommender_system.auth_server.models;

import com.job_recommender_system.auth_server.utils.PaymentStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.OffsetDateTime;

@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(
        name = "payments",
        indexes = {
                @Index(name = "idx_payment_user_id", columnList = "uid")
        }
)
@Getter
@Setter
public class Payment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long paymentId;

    @ManyToOne
    @JoinColumn(
            name = "uid",
            nullable = false,
            foreignKey = @ForeignKey(name = "fk_payment_user")
    )
    private User user;

    @Column(nullable = false)
    private Long amount;

    @Column(nullable = false)
    private String currency;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private PaymentStatus status; //"PENDING", "PAID", "FAILED"

    @Column(nullable = false)
    private String provider;

    @Column(nullable = false)
    private String providerPaymentRef;

    @Column(nullable = false)
    private OffsetDateTime createdAt;

    @Column(nullable = false)
    private OffsetDateTime updatedAt;
}