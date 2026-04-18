package com.job_recommender_system.auth_server.models;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(
        name = "payment_metadata",
        indexes = {
                @Index(name = "idx_payment_metadata_payment_id", columnList = "payment_id")
        }
)
@Getter
@Setter
public class PaymentMetadata {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(
            name = "payment_id",
            referencedColumnName = "paymentId",
            nullable = false,
            foreignKey = @ForeignKey(name = "fk_payment_metadata_payment"))
    private Payment payment;

    @Column(name = "meta_key", nullable = false)
    private String key;

    @Column(name = "meta_value", nullable = false)
    private String value;
}
