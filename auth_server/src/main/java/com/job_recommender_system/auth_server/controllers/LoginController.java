package com.job_recommender_system.auth_server.controllers;

import com.job_recommender_system.auth_server.dto.LoginRequest;
import com.job_recommender_system.auth_server.models.RefreshToken;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.RefreshTokenRepository;
import com.job_recommender_system.auth_server.repositories.UserRepository;
import com.job_recommender_system.auth_server.services.AuthService;
import com.job_recommender_system.auth_server.services.JwtService;
import com.job_recommender_system.auth_server.services.UserService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.Map;

@RestController
@RequestMapping("/auth")
public class LoginController {
    private final AuthService authService;
    private final JwtService jwtService;
    private final UserService userService;
    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    public LoginController(AuthService authService, JwtService jwtService,
                           UserRepository userRepository, UserService userService,
                           RefreshTokenRepository refreshTokenRepository) {
        this.authService = authService;
        this.jwtService = jwtService;
        this.userRepository = userRepository;
        this.userService = userService;
        this.refreshTokenRepository = refreshTokenRepository;
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
            /*
            * - Store the access token in database to avoid reusing the same access token for logout multiple times
            * - Delete these tokens from database after the expiry time of the access token is reached to avoid memory leak
            * - Do this the same for refresh token as well, store the refresh token in database and delete it after the expiry time is reached or when the user logs out
            * */


            token = token.replace("Bearer ", "");
            String userEmail = jwtService.extractUsername(token);
            User user = userRepository.findByEmail(userEmail)
                    .orElseThrow(() -> new RuntimeException("User not found"));
            Long uid = user.getUid();
            // Get the refresh token from the database associated with the user and revoke is 0
            String refreshToken = refreshTokenRepository.findByUidAndRevoked(uid, false)
                    .orElseThrow(() -> new RuntimeException("Refresh token not found or already revoked")).getRefreshToken();

            System.out.println(refreshToken);

            authService.logout(refreshToken);
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

    @GetMapping("/oauth2/success")
    public ResponseEntity<String> success(Authentication authentication) {
        if (authentication == null || !(authentication.getPrincipal() instanceof OidcUser oidcUser)) {
            return ResponseEntity.status(401).body("No authentication found");
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
        return ResponseEntity.ok(accessToken);
    }

    @GetMapping("/oauth2/failure")
    public ResponseEntity<String> oauth2LoginFailure() {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Login failed.");
    }
}
