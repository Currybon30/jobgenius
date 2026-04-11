package com.job_recommender_system.auth_server.services;

import com.job_recommender_system.auth_server.dto.AuthResponse;
import com.job_recommender_system.auth_server.dto.LoginRequest;
import com.job_recommender_system.auth_server.dto.RegisterRequest;
import com.job_recommender_system.auth_server.models.RefreshToken;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.RefreshTokenRepository;
import com.job_recommender_system.auth_server.repositories.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Date;

@RequiredArgsConstructor
@Service
public class AuthService {

    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final RedisService redisService;

    public void register(RegisterRequest registerRequest) {
        try {
            User user = userRepository.findByEmail(registerRequest.getEmail()).orElse(null);

            if(user != null) {
                if ("GOOGLE".equals(user.getProvider())) {
                    // MERGE: enable password login too
                    user.setPassword(passwordEncoder.encode(registerRequest.getPassword()));
                    user.setProvider("BOTH");
                }
                userRepository.save(user);
            }

            else {
                User newUser = new User();
                newUser.setName(registerRequest.getName());
                newUser.setEmail(registerRequest.getEmail());
                newUser.setPassword(passwordEncoder.encode(registerRequest.getPassword()));
                // save user to database
                userRepository.save(newUser);
            }
        }
        catch (Exception e) {
            throw new RuntimeException("Error registering user: " + e.getMessage());
        }
    }

    public AuthResponse login(LoginRequest loginRequest) {
        try {
            User user = userRepository.findByEmail(loginRequest.getEmail())
                .orElseThrow(() -> new RuntimeException("User not found"));
            if (user.getPassword().equals("OAUTH2_USER") || "GOOGLE".equals(user.getProvider()) || user.getPassword() == null) {
                throw new RuntimeException("Error occurred during login. Please try again.");
            }
            if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPassword())) {
                throw new RuntimeException("Invalid password");
            }
            // Generate access token
            String accessToken = jwtService.generateAccessToken(user);
            String refreshTokenStr = jwtService.generateRefreshToken(user);

            // Generate refresh token
            RefreshToken refreshToken = new RefreshToken();
            refreshToken.setRefreshToken(refreshTokenStr);
            refreshToken.setUid(user.getUid());
            refreshToken.setRevoked(false);
            refreshToken.setCreatedAt(new Date());
            refreshToken.setExpiryDate(new Date(System.currentTimeMillis() + 1000L * 60 * 60 * 24 * 7)); // 7 days
            refreshToken.setSessionStartAt(new Date());
            refreshTokenRepository.save(refreshToken);
            return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshTokenStr)
                .errorMessage("")
                .build();
        } catch (Exception e) {
            throw new RuntimeException("Error logging in user: " + e.getMessage());
        }
    }

    public void logout(String accessToken, String refreshToken) {
        try {
            // Store access token in redis with expiry same as token expiry
            accessToken = accessToken.replace("Bearer ", ""); // Remove "Bearer " prefix if present
            long ttl = jwtService.extractExpiration(accessToken).getTime() - System.currentTimeMillis();
            redisService.addToBlacklist(accessToken, ttl);

            // Revoke refresh token in database
            refreshToken = refreshToken.replace("Bearer ", ""); // Remove "Bearer " prefix if present
            RefreshToken token = refreshTokenRepository.findByRefreshToken(refreshToken)
                .orElseThrow(() -> new RuntimeException("Invalid token"));
            token.setRevoked(true);
            refreshTokenRepository.save(token);
        } catch (Exception e) {
            throw new RuntimeException("Error logging out user: " + e.getMessage());
        }
    }
}