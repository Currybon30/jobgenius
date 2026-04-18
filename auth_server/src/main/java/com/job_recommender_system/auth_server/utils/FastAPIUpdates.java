package com.job_recommender_system.auth_server.utils;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Map;

@Component
@RequiredArgsConstructor
public class FastAPIUpdates {
    private final WebClient webClient;
    private final Logger logger = LoggerFactory.getLogger(FastAPIUpdates.class);
    public void updatePlanFastAPI(String userId, String newPlan, String newPlanExpiry) {
        try {
            webClient.put()
                    .uri(uriBuilder -> uriBuilder
                            .path("/internal/users/{user_id}/plan/update")
                            .build(userId))
                    .bodyValue(
                            Map.of("plan", newPlan,
                                    "plan_expiry", newPlanExpiry)
                    )
                    .retrieve()
                    .bodyToMono(Void.class)
                    .block();
            logger.info("Successfully updated plan for user {} to {} with expiry {} in FastAPI", userId, newPlan, newPlanExpiry);
        } catch (Exception e) {
            logger.error("Failed to update plan for user {}: {}", userId, e.getMessage());
        }
    }
}
