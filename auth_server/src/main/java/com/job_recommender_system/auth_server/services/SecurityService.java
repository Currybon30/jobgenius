package com.job_recommender_system.auth_server.services;

import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import com.job_recommender_system.auth_server.repositories.UserRepository;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@Service
public class SecurityService {
    private final UserRepository userRepository;

    public boolean isOwner(Long uid) {
        String username = (String) SecurityContextHolder.getContext()
                .getAuthentication()
                .getPrincipal();
        return userRepository.findById(uid)
                .map(user -> user.getEmail().equals(username))
                .orElse(false);
    }
}
