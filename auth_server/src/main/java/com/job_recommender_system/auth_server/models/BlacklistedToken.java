package com.job_recommender_system.auth_server.models;

import jakarta.persistence.*;

@Entity
@Table(name = "blacklisted_tokens")
public class BlacklistedToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long bltid;

    @Column(nullable = false, unique = true)
    private String bltoken;

    public BlacklistedToken() {}
    public BlacklistedToken(String bltoken) {
        this.bltoken = bltoken;
    }

    public String getBltoken() {
        return bltoken;
    }

    public void setBltoken(String bltoken) {
        this.bltoken = bltoken;
    }
}
