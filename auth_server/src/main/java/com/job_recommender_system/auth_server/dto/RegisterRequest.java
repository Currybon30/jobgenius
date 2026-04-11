package com.job_recommender_system.auth_server.dto;

public class RegisterRequest {
    private String name;
    private String email;
    private String password;
    public String getName() {
        return name;
    }
    public String getEmail() {
        return email;
    }
    public String getPassword() {
        return password;
    }
}
