package com.job_recommender_system.auth_server.repositories;

import com.job_recommender_system.auth_server.models.RefreshToken;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Date;
import java.util.List;
import java.util.Optional;

public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {
    Optional<RefreshToken> findByRefreshToken(String refreshToken);

    List<RefreshToken> findByUser_Uid(Long uid);

    List<RefreshToken> findByUser_UidAndRevokedFalse(Long uid);

    int deleteByExpiryDateBeforeAndRevoked(Date date, boolean revoked);

}
