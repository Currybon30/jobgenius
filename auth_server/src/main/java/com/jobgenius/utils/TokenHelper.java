package com.jobgenius.utils;

import com.jobgenius.models.RefreshToken;
import com.jobgenius.models.User;
import com.jobgenius.repositories.RefreshTokenRepository;
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
