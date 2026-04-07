package com.job_recommender_system.auth_server.repositories;

import com.job_recommender_system.auth_server.models.BlacklistedToken;
import org.springframework.data.jpa.repository.JpaRepository;

public interface BlacklistedTokenRepository extends JpaRepository<BlacklistedToken, Long> {
    boolean existsByBltoken(String bltoken);

}
