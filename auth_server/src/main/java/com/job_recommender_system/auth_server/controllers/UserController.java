package com.job_recommender_system.auth_server.controllers;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.services.SecurityService;
import com.job_recommender_system.auth_server.services.UserService;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@RestController
@RequestMapping("/api")
public class UserController {
    private final UserService userService;
    private final SecurityService securityService;

    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/users")
    public ResponseEntity<List<User>> getAllUsers(Authentication auth) {
        System.out.println(auth.getAuthorities());
        List<User> users = userService.getAllUsers();
        return ResponseEntity.ok(users);
    }

    @PreAuthorize("isAuthenticated()")
    @GetMapping("/users/{uid}")
    public ResponseEntity<?> getUserById(@PathVariable Long uid) {
        if (securityService.isOwner(uid)) {
            User user = userService.getUserById(uid);
            return ResponseEntity.ok(user);
        } else {
            User user = userService.getUserById(uid);
            if (user == null) {
                return ResponseEntity.status(404).body("User not found with id: " + uid);
            }
            String name = user.getName();
            return ResponseEntity.status(403)
                    .body("Access denied. You are not authorized to access user " + name + "'s information.");
        }
    }

    @GetMapping("/users/me")
    public ResponseEntity<User> getCurrentUser(Authentication auth) {
        User user = userService.getUserByEmail((String) auth.getPrincipal());
        return ResponseEntity.ok(user);
    }
}
