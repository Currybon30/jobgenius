package com.job_recommender_system.auth_server.services;

import com.job_recommender_system.auth_server.repositories.BlacklistedTokenRepository;
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

    public JwtService() {
        if (SECRET_KEY == null || SECRET_KEY.isEmpty()) {
            throw new IllegalStateException("JWT_SECRET_KEY environment variable is not set");
        }
    }

    private Key getKey() {
        return Keys.hmacShaKeyFor(Decoders.BASE64.decode(SECRET_KEY));
    }

    public String generateAccessToken(String username) {
        return Jwts.builder()
                .setSubject(username)
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

    public String generateRefreshToken(String username) {
        return Jwts.builder()
                .setSubject(username)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 1000 * 60 * 60 * 24 * 7)) // 7 days
                .signWith(getKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    public String refreshAccessToken(String refreshToken) {
        if (validateToken(refreshToken)) {
            String username = extractUsername(refreshToken);
            return generateAccessToken(username);
        }
        throw new RuntimeException("Invalid refresh token");
    }

    public boolean isTokenBlacklisted(String token, BlacklistedTokenRepository blacklistedTokenRepo) {
        return blacklistedTokenRepo.existsByBltoken(token);
    }
}
