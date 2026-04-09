package com.job_recommender_system.auth_server.config;

import com.job_recommender_system.auth_server.security.JwtAuthFilter;
import com.job_recommender_system.auth_server.security.RateLimitingFilter;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfigurationSource;

@Configuration
public class SecurityConfig {

    private final JwtAuthFilter jwtAuthFilter;
    private final RateLimitingFilter rateLimitingFilter;

    public SecurityConfig(JwtAuthFilter jwtAuthFilter, RateLimitingFilter rateLimitingFilter) {
        this.jwtAuthFilter = jwtAuthFilter;
        this.rateLimitingFilter = rateLimitingFilter;
    }

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
                .requestMatchers("/auth/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2Login(oauth2 -> oauth2
                .loginPage("/auth/oauth2/login") // Custom login page for OAuth2
                .defaultSuccessUrl("/auth/oauth2/success", true) // Redirect after successful OAuth2 login. True means always redirect to this URL after login, regardless of the original request.
                .failureUrl("/auth/oauth2/failure") // Redirect after failed OAuth2 login
            )
            .addFilterBefore(rateLimitingFilter, JwtAuthFilter.class) // Add rate limiting filter before JWT authentication filter
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
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
}
