package com.job_recommender_system.auth_server.controllers;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
public class HealthCheck {
    @RequestMapping("/health")
    public String healthCheck() {
        return "Auth Server is healthy!";
    }
}
