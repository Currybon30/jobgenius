package com.job_recommender_system.auth_server.security;

import io.github.bucket4j.BucketConfiguration;
import io.github.bucket4j.distributed.proxy.ProxyManager;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.function.Supplier;

@Component
public class RateLimitingFilter extends OncePerRequestFilter {
    private final ProxyManager<String> proxyManager;
    private final Supplier<BucketConfiguration> bucketConfigurationSupplier;

    public RateLimitingFilter(ProxyManager<String> proxyManager, Supplier<BucketConfiguration> bucketConfigurationSupplier) {
        this.proxyManager = proxyManager;
        this.bucketConfigurationSupplier = bucketConfigurationSupplier;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws IOException, ServletException {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty()) {
            ip = request.getRemoteAddr();
        } else {
            // X-Forwarded-For can contain multiple IPs; the first one is the client
            ip = ip.split(",")[0].trim();
        }
        var bucket = proxyManager.builder().build(ip, bucketConfigurationSupplier); // Get or create bucket for the client's IP address

        if (bucket.tryConsume(1)) { // Consume 1 token for the request
            filterChain.doFilter(request, response); // Allow request to proceed
        } else {
            response.setStatus(429); // Too Many Requests
            response.setHeader("Retry-After", "120"); // Suggest client to retry after 120 seconds
        }
    }
}
