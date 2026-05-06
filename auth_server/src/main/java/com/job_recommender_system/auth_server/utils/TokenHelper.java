package com.job_recommender_system.auth_server.utils;

import java.util.List;

import org.springframework.stereotype.Component;

import com.job_recommender_system.auth_server.models.RefreshToken;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.RefreshTokenRepository;

import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class TokenHelper {
    private RefreshTokenRepository refreshTokenRepository;

    // Revoke all refresh tokens for the user
    public void refreshTokenList(User user) {
        List<RefreshToken> refreshTokenList = refreshTokenRepository.findByUser_UidAndRevokedFalse(user.getUid())
                .orElse(List.of());
        if (!refreshTokenList.isEmpty()) {
            refreshTokenList.forEach(token -> token.setRevoked(true));
            refreshTokenRepository.saveAll(refreshTokenList);
        }
    }
}
