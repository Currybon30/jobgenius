package com.job_recommender_system.auth_server.repositories;

import java.util.Date;
import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.job_recommender_system.auth_server.models.RefreshToken;

public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {
    Optional<RefreshToken> findByRefreshToken(String refreshToken);

    Optional<List<RefreshToken>> findByUser_UidAndRevokedFalse(Long uid);

    int deleteByExpiryDateBeforeAndRevoked(Date date, boolean revoked);

}
