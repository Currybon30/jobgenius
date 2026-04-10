package com.job_recommender_system.auth_server.repositories;

import com.job_recommender_system.auth_server.models.RefreshToken;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {
    Optional<RefreshToken> findByRefreshToken(String refreshToken);
    Optional<RefreshToken> findByUidAndRevoked(Long uid, boolean revoked);

}
