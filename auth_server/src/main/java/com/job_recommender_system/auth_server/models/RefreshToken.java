package com.job_recommender_system.auth_server.models;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.util.Date;

@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "refresh_tokens")
public class RefreshToken {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, unique = true)
    private String refreshToken;

    @ManyToOne
    @JoinColumn(
            name = "uid",
            nullable = false,
            foreignKey = @ForeignKey(name = "fk_refresh_token_user")
    )
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
