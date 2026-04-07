package com.job_recommender_system.auth_server.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import com.job_recommender_system.auth_server.models.User;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    Boolean existsByEmail(String email);
}
