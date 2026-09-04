package com.jobgenius.repositories;

import java.util.Date;
import java.util.List;
import java.util.Optional;

import com.jobgenius.models.RefreshToken;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {
    Optional<RefreshToken> findByRefreshToken(String refreshToken);

    List<RefreshToken> findByUser_Uid(Long uid);

    List<RefreshToken> findByUser_UidAndRevokedFalse(Long uid);

    int deleteByExpiryDateBeforeAndRevoked(Date date, boolean revoked);

}
