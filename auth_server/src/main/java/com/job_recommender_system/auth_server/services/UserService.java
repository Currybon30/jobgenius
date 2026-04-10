package com.job_recommender_system.auth_server.services;

import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.UserRepository;
import jakarta.transaction.Transactional;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.stereotype.Service;

@Service
public class UserService {
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Transactional
    public void saveOrUpdateOAuthUser(OidcUser oidcUser) {
        String email = oidcUser.getEmail();
        userRepository.findByEmail(email)
                .map(existingUser -> {
                    existingUser.setName(oidcUser.getFullName());
                    return userRepository.save(existingUser);
                })
                .orElseGet(() -> {
                    User newUser = new User();
                    newUser.setEmail(email);
                    newUser.setName(oidcUser.getFullName());
                    newUser.setPassword("OAUTH2_USER");
                    newUser.setProvider("GOOGLE");
                    return userRepository.save(newUser);
                });
    }
}