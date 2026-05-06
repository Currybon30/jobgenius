package com.job_recommender_system.auth_server.models;

import java.util.Date;

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
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "refresh_tokens", indexes = {
        @Index(name = "idx_refresh_token", columnList = "refreshToken"),
        @Index(name = "idx_user_id", columnList = "uid")
})
public class RefreshToken {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, unique = true)
    private String refreshToken;

    @ManyToOne
    @JoinColumn(name = "uid", nullable = false, foreignKey = @ForeignKey(name = "fk_refresh_token_user"))
    private User user;

    @Column(nullable = false)
    private boolean revoked;

    @Column(nullable = false)
    private Date createdAt;

    @Column(nullable = false)
    private Date expiryDate;

    @Column(nullable = false)
    private Date sessionStartAt;

    public Long getId() {
        return id;
    }

    public String getRefreshToken() {
        return refreshToken;
    }

    public void setRefreshToken(String refreshToken) {
        this.refreshToken = refreshToken;
    }

    public Long getUserId() {
        return user.getUid();
    }

    public void setUser(User user) {
        this.user = user;
    }

    public boolean isRevoked() {
        return revoked;
    }

    public boolean setRevoked(boolean revoked) {
        this.revoked = revoked;
        return revoked;
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }

    public Date getExpiryDate() {
        return expiryDate;
    }

    public void setExpiryDate(Date expiryDate) {
        this.expiryDate = expiryDate;
    }

    public Date getSessionStartAt() {
        return sessionStartAt;
    }

    public void setSessionStartAt(Date sessionStartAt) {
        this.sessionStartAt = sessionStartAt;
    }

}
