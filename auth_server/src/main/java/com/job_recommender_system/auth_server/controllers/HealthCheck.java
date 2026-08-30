package com.job_recommender_system.auth_server.controllers;

import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CookieValue;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Objects;
import java.util.UUID;

@RestController
@RequestMapping()
public class HealthCheck {
    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        return ResponseEntity.ok("Auth server is up and running!");
    }

    @GetMapping("/anonymous_ready")
    public ResponseEntity<String> anonymousReady(
        @CookieValue(value = "access_token", required = false) String accessToken,
        @CookieValue(value = "anonymous_uuid", required = false) String anonymousUuid,
        HttpServletResponse response) {
        if (accessToken != null) {
            return ResponseEntity.ok("User is already authenticated.");
        }
        if (anonymousUuid != null) {
            return ResponseEntity.ok("Anonymous user already has UUID");
        }
        // Generate random uuid for unauthenticated users
        UUID uuid = UUID.randomUUID();
        // Convert to standard 36-character String representation
        String uuidString = uuid.toString();
        ResponseCookie anonymousUuidCookie = ResponseCookie.from("anonymous_uuid", Objects.requireNonNull(uuidString))
                .httpOnly(true)
                .secure(true)
                .path("/")
                .sameSite("None") // REQUIRED for React cross-origin
                .maxAge(30 * 24 * 60 * 60) // 30 days
                .build();

        response.addHeader(HttpHeaders.SET_COOKIE, anonymousUuidCookie.toString());
        return ResponseEntity.ok("Annonymous ready with UUID: " + uuidString);
    }
}
