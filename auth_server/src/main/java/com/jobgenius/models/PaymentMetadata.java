package com.jobgenius.models;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.ForeignKey;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

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

        @ManyToOne
        @JoinColumn(name = "payment_id", referencedColumnName = "paymentId", nullable = false, foreignKey = @ForeignKey(name = "fk_payment_metadata_payment"))
        private Payment payment;

        @Column(name = "meta_key", nullable = false)
        private String key;

        @Column(name = "meta_value", nullable = false)
        private String value;
}
