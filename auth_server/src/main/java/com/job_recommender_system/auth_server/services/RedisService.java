package com.job_recommender_system.auth_server.services;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.data.redis.core.StringRedisTemplate;

import java.util.concurrent.TimeUnit;

@RequiredArgsConstructor
@Service
public class RedisService {
    private final StringRedisTemplate redisTemplate;

    private static final String BLACKLIST_PREFIX = "blacklist:";

    public void addToBlacklist(String token, long ttl) {
        redisTemplate.opsForValue().set(
            BLACKLIST_PREFIX + token, "1", ttl, TimeUnit.MILLISECONDS
        );
    }

    public boolean isBlacklisted(String token) {
        return Boolean.TRUE.equals(
                redisTemplate.hasKey(BLACKLIST_PREFIX + token)
        );
    }
}
