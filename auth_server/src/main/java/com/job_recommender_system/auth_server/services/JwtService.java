package com.job_recommender_system.auth_server.services;

import com.job_recommender_system.auth_server.models.RefreshToken;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.RefreshTokenRepository;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.security.Key;
import java.util.Date;

@Service
public class JwtService {
    @Value("${jwt.secret}")
    private final String SECRET_KEY = System.getenv("JWT_SECRET_KEY");

    private final RefreshTokenRepository refreshTokenRepository;


    public JwtService(RefreshTokenRepository refreshTokenRepository) {
        this.refreshTokenRepository = refreshTokenRepository;
        if (SECRET_KEY == null || SECRET_KEY.isEmpty()) {
            throw new IllegalStateException("JWT_SECRET_KEY environment variable is not set");
        }
    }

    private Key getKey() {
        return Keys.hmacShaKeyFor(Decoders.BASE64.decode(SECRET_KEY));
    }

    public String generateAccessToken(User user) {
        return Jwts.builder()
                .setSubject(user.getEmail())
                .claim("role", user.getRole()) // Include role in the payload
                .claim("tier", user.getTier()) // Include tier in the payload
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 1000 * 60 * 15)) // 15 minutes
                .signWith(getKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    public String extractUsername(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getKey())
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
    }

    public String extractUserRole(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getKey())
                .build()
                .parseClaimsJws(token)
                .getBody()
                .get("role", String.class);
    }

    public String extractUserTier(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getKey())
                .build()
                .parseClaimsJws(token)
                .getBody()
                .get("tier", String.class);
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                .setSigningKey(getKey())
                .build()
                .parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public String generateRefreshToken(User user) {
        return Jwts.builder()
                .setSubject(user.getEmail())
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 1000 * 60 * 60 * 24 * 7)) // 7 days
                .signWith(getKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    public String refreshAccessToken(String refreshToken, User user) {
        refreshToken = refreshToken.replace("Bearer ", ""); // Remove "Bearer " prefix if present
        RefreshToken token = refreshTokenRepository.findByRefreshToken(refreshToken)
                .orElseThrow(() -> new RuntimeException("Invalid refresh token"));

        if (token.isRevoked() || token.getExpiryDate().before(new Date())) {
            throw new RuntimeException("Refresh token is revoked or expired.");
        }

        if(!validateToken(refreshToken)) {
            throw new RuntimeException("Invalid refresh token");
        }

        token.setRevoked(true); // If the refresh token has been used once, revoke it to prevent reuse
        refreshTokenRepository.save(token);
        long MAX_SESSION_TIME = 30L * 24 * 60 * 60 * 1000; // 30 days

        if (System.currentTimeMillis() - token.getSessionStartAt().getTime() > MAX_SESSION_TIME) {
            throw new RuntimeException("Session expired. Please log in again.");
        }

        // else generate new refresh token
        RefreshToken newToken = new RefreshToken();
        newToken.setRefreshToken(generateRefreshToken(user));
        newToken.setUid(user.getUid());
        newToken.setRevoked(false);
        newToken.setCreatedAt(new Date());
        newToken.setExpiryDate(new Date(System.currentTimeMillis() + 1000L * 60 * 60 * 24 * 7)); // 7 days
        newToken.setSessionStartAt(token.getSessionStartAt()); // Keep the original session start time
        refreshTokenRepository.save(newToken);

        return generateAccessToken(user);
    }
}
