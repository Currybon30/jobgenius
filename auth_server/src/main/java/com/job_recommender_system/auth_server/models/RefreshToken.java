package com.job_recommender_system.auth_server.models;

import jakarta.persistence.*;

import java.util.Date;

@Entity
@Table(name = "refresh_tokens")
public class RefreshToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, unique = true)
    private String refreshToken;

    @Column(nullable = false)
    private Long uid;

    @Column(nullable = false)
    private boolean revoked;

    @Column(nullable = false)
    private Date createdAt;

    @Column(nullable = false)
    private Date expiryDate;

    @Column(nullable = false)
    private Date sessionStartAt;


    public RefreshToken() {}
    public RefreshToken(String refreshToken, Long uid, boolean revoked, Date expiryDate, Date createdAt, Date sessionStartAt) {
        this.refreshToken = refreshToken;
        this.uid = uid;
        this.revoked = revoked;
        this.expiryDate = expiryDate;
        this.createdAt = createdAt;
        this.sessionStartAt = sessionStartAt;
    }

    public Long getId() {
        return id;
    }

    public String getRefreshToken() {
        return refreshToken;
    }

    public void setRefreshToken(String refreshToken) {
        this.refreshToken = refreshToken;
    }

    public Long getUid() {
        return uid;
    }

    public void setUid(Long uid) {
        this.uid = uid;
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
