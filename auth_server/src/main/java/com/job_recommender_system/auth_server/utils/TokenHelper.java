package com.job_recommender_system.auth_server.utils;

import com.job_recommender_system.auth_server.models.RefreshToken;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.RefreshTokenRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;

import java.util.List;

@Component
@RequiredArgsConstructor
public class TokenHelper {
    private static final Logger logger = org.slf4j.LoggerFactory.getLogger(TokenHelper.class);
    private final RefreshTokenRepository refreshTokenRepository;

    // Revoke all refresh tokens for the user
    public void refreshTokenList(User user) {
        logger.info("Revoking all refresh tokens for user: {}", user.getUid());
        List<RefreshToken> refreshTokenList = refreshTokenRepository.findByUser_Uid(user.getUid());

        if (refreshTokenList.isEmpty()) {
            return;
        }
        List<RefreshToken> refreshUnrevokedTokenList = refreshTokenRepository.findByUser_UidAndRevokedFalse(user.getUid());
        if (!refreshUnrevokedTokenList.isEmpty()) {
            refreshUnrevokedTokenList.forEach(token -> token.setRevoked(true));
            refreshTokenRepository.saveAll(refreshUnrevokedTokenList);
        }
    }
}
