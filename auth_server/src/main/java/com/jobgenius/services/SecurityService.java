package com.jobgenius.services;

import com.jobgenius.repositories.UserRepository;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

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
