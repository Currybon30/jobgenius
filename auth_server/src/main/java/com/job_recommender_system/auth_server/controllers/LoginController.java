package com.job_recommender_system.auth_server.controllers;

import com.job_recommender_system.auth_server.dto.LoginRequest;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.UserRepository;
import com.job_recommender_system.auth_server.services.AuthService;
import com.job_recommender_system.auth_server.services.JwtService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/auth")
public class LoginController {
    private final AuthService authService;
    private final JwtService jwtService;
    private final UserRepository userRepository;
    public LoginController(AuthService authService, JwtService jwtService, UserRepository userRepository) {

        this.authService = authService;
        this.jwtService = jwtService;
        this.userRepository = userRepository;
    }
    
    @PostMapping("/login")
    public ResponseEntity<String> login(@RequestBody LoginRequest loginRequest) {
        try {
            String token = authService.login(loginRequest);
            return ResponseEntity.ok(token);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(e.getMessage());
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<String> logout(@RequestHeader("Authorization") String token) {
        try {
            authService.logout(token);
            return ResponseEntity.ok("Logged out successfully");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(e.getMessage());
        }
    }

    @PostMapping("/refresh")
    public ResponseEntity<?> refreshToken(@RequestHeader("Authorization") String refreshToken, @RequestParam("user_email") String userEmail) {
        try {
            User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new RuntimeException("User not found"));
            String newToken = jwtService.refreshAccessToken(refreshToken, user);
            return ResponseEntity.ok(newToken);
        } catch (Exception e) {
            String message = e.getMessage();

            if (message.equals("Session expired. Please log in again.")) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "SESSION_EXPIRED"));
            }

            if (message.equals("Refresh token is revoked or expired.")) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "REFRESH_TOKEN_EXPIRED"));
            }

            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "INVALID_TOKEN"));
        }
    }
}
