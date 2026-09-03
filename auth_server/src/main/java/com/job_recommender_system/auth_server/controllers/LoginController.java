package com.job_recommender_system.auth_server.controllers;

import com.job_recommender_system.auth_server.dto.LoginRequest;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.UserRepository;
import com.job_recommender_system.auth_server.services.AuthService;
import com.job_recommender_system.auth_server.services.JwtService;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Objects;

@RequiredArgsConstructor
@RestController
@RequestMapping("/auth")
public class LoginController {
    private final AuthService authService;
    private final JwtService jwtService;
    private final UserRepository userRepository;

    private final Logger logger = LoggerFactory.getLogger(LoginController.class);

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest loginRequest, HttpServletResponse response) {
        try {
            Map<String, String> tokens = authService.login(loginRequest);
            String accessToken = tokens.get("accessToken");
            String refreshToken = tokens.get("refreshToken");
            ResponseCookie cookie = ResponseCookie.from("access_token", Objects.requireNonNull(accessToken))
                    .httpOnly(true)
                    .secure(true)
                    .path("/")
                    .sameSite("None") // REQUIRED for React cross-origin
                    .maxAge( 15 * 60)
                    .build();

            ResponseCookie refreshCookie = ResponseCookie.from("refresh_token", Objects.requireNonNull(refreshToken))
                    .httpOnly(true)
                    .secure(true)
                    .path("/auth/refresh") // 🔥 more restricted than "/"
                    .sameSite("None")
                    .maxAge(7 * 24 * 60 * 60) // 7 days
                    .build();

            // remove anonymousUuid from cookie
            ResponseCookie anonymousUuid = ResponseCookie.from("anonymous_uuid", "")
                    .httpOnly(true)
                    .secure(true)
                    .path("/")
                    .sameSite("None") // REQUIRED for React cross-origin
                    .maxAge(0)
                    .build();

            response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
            response.addHeader(HttpHeaders.SET_COOKIE, refreshCookie.toString());
            response.addHeader(HttpHeaders.SET_COOKIE, anonymousUuid.toString());

            return ResponseEntity.ok("Login successful");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                "error", "LOGIN_FAILED",
                "message", e.getMessage()
            ));
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<String> logout(@CookieValue(name = "access_token", required = false) String accessToken,
            HttpServletResponse response) {
        try {
            authService.logout(accessToken);

            ResponseCookie cookie = ResponseCookie.from("access_token", "")
                    .httpOnly(true)
                    .secure(true)
                    .path("/")
                    .sameSite("None") // REQUIRED for React cross-origin
                    .maxAge(0)
                    .build();

            ResponseCookie refreshCookie = ResponseCookie.from("refresh_token", "")
                    .httpOnly(true)
                    .secure(true)
                    .path("/auth/refresh") // 🔥 more restricted than "/"
                    .sameSite("None")
                    .maxAge(0)
                    .build();

            response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
            response.addHeader(HttpHeaders.SET_COOKIE, refreshCookie.toString());
            return ResponseEntity.ok("Logged out successfully");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(e.getMessage());
        }
    }

    @PostMapping("/refresh")
    public ResponseEntity<?> refreshToken(@CookieValue(name = "refresh_token", required = false) String refreshToken,
            HttpServletResponse response) {
        try {
            String userEmail = jwtService.extractUsername(refreshToken);
            User user = userRepository.findByEmail(userEmail)
                    .orElseThrow(() -> new RuntimeException("User not found"));
            Map<String, String> tokens = jwtService.refreshAccessToken(refreshToken, user);

            String newAccessToken = tokens.get("access_token");
            String newRefreshToken = tokens.get("refresh_token");

            System.out.println("New Access Token: " + newAccessToken);


            ResponseCookie cookie = ResponseCookie.from("access_token", Objects.requireNonNull(newAccessToken))
                    .httpOnly(true)
                    .secure(true)
                    .path("/")
                    .sameSite("None") // REQUIRED for React cross-origin
                    .maxAge(15 * 60) // 15 minutes
                    .build();

            ResponseCookie refreshCookie = ResponseCookie.from("refresh_token", Objects.requireNonNull(newRefreshToken))
                    .httpOnly(true)
                    .secure(true)
                    .path("/auth/refresh") // 🔥 more restricted than "/"; // Meaning: only send this cookie when the request is made to /auth/refresh endpoint
                    .sameSite("None")
                    .maxAge(7 * 24 * 60 * 60) // 7 days
                    .build();

            response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
            response.addHeader(HttpHeaders.SET_COOKIE, refreshCookie.toString());
            return ResponseEntity.ok("Access token refreshed successfully");
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

    @GetMapping("/oauth2/failure")
    public ResponseEntity<?> oauth2LoginFailure() {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                "error", "LOGIN_FAILED",
                "message", "OAuth2 login failed. Please try again."
        ));
    }
}
