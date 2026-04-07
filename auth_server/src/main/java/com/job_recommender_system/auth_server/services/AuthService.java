package com.job_recommender_system.auth_server.services;

import com.job_recommender_system.auth_server.dto.LoginRequest;
import com.job_recommender_system.auth_server.dto.RegisterRequest;
import com.job_recommender_system.auth_server.models.BlacklistedToken;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.BlacklistedTokenRepository;
import com.job_recommender_system.auth_server.repositories.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class AuthService {

    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;

    private final BlacklistedTokenRepository blacklistedTokenRepository;

    public AuthService(JwtService jwtService, PasswordEncoder passwordEncoder, UserRepository userRepository, BlacklistedTokenRepository blacklistedTokenRepository) {
        this.jwtService = jwtService;
        this.passwordEncoder = passwordEncoder;
        this.userRepository = userRepository;
        this.blacklistedTokenRepository = blacklistedTokenRepository;
    }

    public void register(RegisterRequest registerRequest) {
        try {
            User user = new User(
            registerRequest.getName(),
            registerRequest.getEmail(),
            passwordEncoder.encode(registerRequest.getPassword())
            );
            // save user to database
            userRepository.save(user);
        }
        catch (Exception e) {
            throw new RuntimeException("Error registering user: " + e.getMessage());
        }
    }

    public Map login(LoginRequest loginRequest) {
        try {
            User user = userRepository.findByEmail(loginRequest.getEmail())
                .orElseThrow(() -> new RuntimeException("User not found"));
            if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPassword())) {
                throw new RuntimeException("Invalid password");
            }
            Map<String, String> tokens = new HashMap<>();
            tokens.put("accessToken", jwtService.generateAccessToken(user.getEmail()));
            tokens.put("refreshToken", jwtService.generateRefreshToken(user.getEmail()));
            return tokens;
        } catch (Exception e) {
            throw new RuntimeException("Error logging in user: " + e.getMessage());
        }
    }

    public void logout(String token) {
        try {
            // Add token to blacklist
            jwtService.validateToken(token);
            token = token.replace("Bearer ", ""); // Remove "Bearer " prefix if present
            BlacklistedToken blacklistedToken = new BlacklistedToken(token);
            blacklistedTokenRepository.save(blacklistedToken);
        } catch (Exception e) {
            throw new RuntimeException("Error logging out user: " + e.getMessage());
        }
    }

    public String refreshAccessToken(String refreshToken) {
        try {
            return jwtService.refreshAccessToken(refreshToken);
        } catch (Exception e) {
            throw new RuntimeException("Error refreshing access token: " + e.getMessage());
        }
    }
}
