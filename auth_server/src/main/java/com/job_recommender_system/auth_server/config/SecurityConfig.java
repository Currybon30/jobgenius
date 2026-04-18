package com.job_recommender_system.auth_server.config;

import com.job_recommender_system.auth_server.models.RefreshToken;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.RefreshTokenRepository;
import com.job_recommender_system.auth_server.repositories.UserRepository;
import com.job_recommender_system.auth_server.security.APIKeyFilter;
import com.job_recommender_system.auth_server.security.JwtAuthFilter;
import com.job_recommender_system.auth_server.security.RateLimitingFilter;
import com.job_recommender_system.auth_server.services.JwtService;
import com.job_recommender_system.auth_server.services.UserService;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.client.oidc.userinfo.OidcUserRequest;
import org.springframework.security.oauth2.client.oidc.userinfo.OidcUserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserService;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Date;
import java.util.List;

@RequiredArgsConstructor
@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    private final JwtAuthFilter jwtAuthFilter;
    private final RateLimitingFilter rateLimitingFilter;
    private final UserService userService;
    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final JwtService jwtService;
    private final APIKeyFilter apiKeyFilter;
    private final WebClient webClient;
    private final Logger logger = LoggerFactory.getLogger(SecurityConfig.class);

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    //CORS config:
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        org.springframework.web.cors.CorsConfiguration configuration = new org.springframework.web.cors.CorsConfiguration();
        configuration.setAllowedOrigins(java.util.List.of("http://localhost:3000")); // Adjust as needed for frontend URL
        configuration.setAllowedMethods(java.util.List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(java.util.List.of("Authorization", "Content-Type"));
        configuration.setAllowCredentials(true);
        org.springframework.web.cors.UrlBasedCorsConfigurationSource source = new org.springframework.web.cors.UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/auth/**", "/api/stripe/webhook").permitAll() // Allow unauthenticated access to auth endpoints and Stripe webhook
                .anyRequest().authenticated()
            )
            .oauth2Login(oauth2 -> oauth2
                    .userInfoEndpoint(userInfo ->
                            userInfo.oidcUserService(oidcUserService())
                    )
                    .successHandler((req, res, auth) -> {
                        OidcUser oidcUser = (OidcUser) auth.getPrincipal();
                        String email = oidcUser.getEmail();
                        User user = userRepository.findByEmail(email)
                                .orElseThrow(() -> new RuntimeException("User not found"));

                        // Generate access token
                        String accessToken = jwtService.generateAccessToken(user);

                        List<RefreshToken> refreshTokenList = refreshTokenRepository.findByUser_UidAndRevokedFalse(user.getUid()).orElse(List.of());
                        if(!refreshTokenList.isEmpty()) {
                            refreshTokenList.forEach(token -> {
                                token.setRevoked(true);
                                refreshTokenRepository.save(token);
                            });
                        }

                        // Generate refresh token
                        RefreshToken refreshToken = new RefreshToken();
                        refreshToken.setRefreshToken(jwtService.generateRefreshToken(user));
                        refreshToken.setUser(user);
                        refreshToken.setRevoked(false);
                        refreshToken.setCreatedAt(new Date());
                        refreshToken.setExpiryDate(new Date(System.currentTimeMillis() + 1000L * 60 * 60 * 24 * 7)); // 7 days
                        refreshToken.setSessionStartAt(new Date());
                        refreshTokenRepository.save(refreshToken);

                        // Return JSON response
                        res.setStatus(HttpServletResponse.SC_OK);
                        res.setContentType("application/json");
                        res.setCharacterEncoding("UTF-8");
                        res.getWriter().write(
                                "{"
                                        + "\"accessToken\":\"" + accessToken + "\","
                                        + "\"refreshToken\":\"" + refreshToken.getRefreshToken() + "\""
                                        + "}"
                        );
                    })
                .failureUrl("/auth/oauth2/failure") // Redirect after failed OAuth2 login
            )
            .addFilterBefore(rateLimitingFilter, UsernamePasswordAuthenticationFilter.class) // Add rate limiting filter before JWT authentication filter
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .addFilterBefore(apiKeyFilter, UsernamePasswordAuthenticationFilter.class)
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((req, res, e) ->
                    res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Unauthorized"))
                .accessDeniedHandler((req, res, e) ->
                    res.sendError(HttpServletResponse.SC_FORBIDDEN, "Forbidden"))
            )
            // Explanation: Disable default HTTP Basic auth, since we're using JWTs for authentication. This prevents browsers from showing a login dialog when accessing protected endpoints without a valid token.
            .httpBasic(httpBasic -> httpBasic.disable())

            // Explanation: Disable form-based login, as we are not using traditional username/password form authentication. This ensures that Spring Security does not attempt to handle login requests with a form, which is unnecessary in a JWT-based stateless authentication setup.
            .formLogin(formLogin -> formLogin.disable())

            // Explanation: Disable logout functionality, since in a stateless JWT authentication system, there is no server-side session to invalidate. Logout can be handled on the client side by simply deleting the JWT token.
            .logout(logout -> logout.disable())

            .cors(cors -> cors.configurationSource(corsConfigurationSource())); // Enable CORS with the defined configuration
        return http.build();
    }


    // ---------------- OAuth 2.0 Login Configuration ----------------
    @Bean
    public OAuth2UserService<OidcUserRequest, OidcUser> oidcUserService() {

        OidcUserService delegate = new OidcUserService();

        return userRequest -> {
            OidcUser oidcUser = delegate.loadUser(userRequest);

            userService.saveOrUpdateOAuthUser(oidcUser);

            return oidcUser;
        };
    }
}
