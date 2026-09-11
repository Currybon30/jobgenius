package com.jobgenius.models;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.OffsetDateTime;

@Entity
@Table(name = "payment_metadata", indexes = {
                @Index(name = "idx_payment_metadata_payment_id", columnList = "payment_id")
})
@Getter
@Setter
public class PaymentMetadata {

        @Id
        @GeneratedValue(strategy = GenerationType.IDENTITY)
        private Long id;

        @Column(nullable = false)
        private Long amount;

        @Column(nullable = false)
        private String currency;

        @OneToOne
        @JoinColumn(name = "payment_id", referencedColumnName = "paymentId", nullable = false, foreignKey = @ForeignKey(name = "fk_payment_metadata_payment"))
        private Payment payment;

        @Column(name = "payment_metadata_key", nullable = false)
        private String key;

        @Column(name = "payment_metadata_value", nullable = false)
        private String value;

        @Column
        private OffsetDateTime periodEnd;
}
