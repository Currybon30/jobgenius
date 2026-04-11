package com.job_recommender_system.auth_server.controllers;

import com.job_recommender_system.auth_server.dto.AuthResponse;
import com.job_recommender_system.auth_server.dto.LoginRequest;
import com.job_recommender_system.auth_server.models.RefreshToken;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.RefreshTokenRepository;
import com.job_recommender_system.auth_server.repositories.UserRepository;
import com.job_recommender_system.auth_server.services.AuthService;
import com.job_recommender_system.auth_server.services.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.Map;

@RequiredArgsConstructor
@RestController
@RequestMapping("/auth")
public class LoginController {
    private final AuthService authService;
    private final JwtService jwtService;
    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody LoginRequest loginRequest) {
        try {
            return ResponseEntity.ok(authService.login(loginRequest));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(
                    AuthResponse.builder()
                            .accessToken(null)
                            .refreshToken(null)
                            .errorMessage(e.getMessage())
                            .build()
            );
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<String> logout(@RequestHeader("Authorization") String accessToken, @RequestBody Map<String, String> refreshTokenRequest) {
        try {
            authService.logout(accessToken, refreshTokenRequest.get("refresh_token"));
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
            return ResponseEntity.ok(jwtService.refreshAccessToken(refreshToken, user));
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

    @GetMapping("/oauth2/success")
    public ResponseEntity<AuthResponse> success(Authentication authentication) {
        if (authentication == null || !(authentication.getPrincipal() instanceof OidcUser oidcUser)) {
            return ResponseEntity.status(401).body(AuthResponse.builder()
                    .accessToken(null)
                    .refreshToken(null)
                    .errorMessage("Authentication failed")
                    .build());
        }

        String email = oidcUser.getEmail();

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        // Generate access token
        String accessToken = jwtService.generateAccessToken(user);

        // Generate refresh token
        RefreshToken refreshToken = new RefreshToken();
        refreshToken.setRefreshToken(jwtService.generateRefreshToken(user));
        refreshToken.setUid(user.getUid());
        refreshToken.setRevoked(false);
        refreshToken.setCreatedAt(new Date());
        refreshToken.setExpiryDate(new Date(System.currentTimeMillis() + 1000L * 60 * 60 * 24 * 7)); // 7 days
        refreshToken.setSessionStartAt(new Date());
        refreshTokenRepository.save(refreshToken);
        return ResponseEntity.ok(AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken.getRefreshToken())
                .errorMessage(null)
                .build());
    }

    @GetMapping("/oauth2/failure")
    public ResponseEntity<String> oauth2LoginFailure() {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Login failed.");
    }
}
