package com.job_recommender_system.auth_server.security;

import com.job_recommender_system.auth_server.services.JwtService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
public class JwtAuthFilter extends OncePerRequestFilter {
    private final JwtService jwtservice;

    public JwtAuthFilter(JwtService jwtservice) {
        this.jwtservice = jwtservice;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) 
        throws ServletException, IOException {
        String path = request.getServletPath();
        if(path.startsWith("/auth/")) { // Skip authentication for /auth/** endpoints
            filterChain.doFilter(request, response);
            return;
        }


        // If already authenticated, skip
        if (SecurityContextHolder.getContext().getAuthentication() != null) {
            filterChain.doFilter(request, response);
            return;
        }

        String authHeader = request.getHeader("Authorization");
        

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            // Invalid authorization header
            filterChain.doFilter(request, response);
            return;
        }
        String token = authHeader.substring(7); // Remove "Bearer " prefix

        try {
            if (jwtservice.validateToken(token)) {
                String username = jwtservice.extractUsername(token);
                String role = jwtservice.extractUserRole(token);
                List<GrantedAuthority> authorities = List.of(
                    new SimpleGrantedAuthority("ROLE_" + role)
                );
                UsernamePasswordAuthenticationToken authenticationToken = new UsernamePasswordAuthenticationToken(username, null, authorities);
                SecurityContextHolder.getContext().setAuthentication(authenticationToken);
            }
        } catch (Exception e) {
            // 🔒 DO NOT expose error to client
            // optionally log: logger.warn("Invalid JWT", e);
        }
        filterChain.doFilter(request, response);
    }
    
}
