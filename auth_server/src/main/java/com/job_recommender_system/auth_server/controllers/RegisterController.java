package com.job_recommender_system.auth_server.controllers;

import com.job_recommender_system.auth_server.dto.RegisterRequest;
import com.job_recommender_system.auth_server.services.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RequiredArgsConstructor
@RestController
@RequestMapping("/auth")
public class RegisterController {

    private final AuthService authService;

    @PostMapping("/register")
    public ResponseEntity<?> signup(@RequestBody RegisterRequest userInfo) {
        // Advanced: Use third-party to register user
        try {
            authService.register(userInfo);
            return ResponseEntity.status(HttpStatus.CREATED).body("User registered successfully");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of(
                        "error", "REGISTRATION_FAILED",
                        "message", e.getMessage()));
        }
    }
}
