package com.jobgenius.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {
    @Value("${API_KEY}")
    private String apiKey;

    @Value("${FASTAPI_URL}")
    private String fastapiUrl;

    @Bean
    public WebClient webClient() {
        return WebClient.builder()
                .baseUrl(fastapiUrl) // Base URL for the job recommendation service
                .defaultHeader("Content-Type", "application/json")
                .defaultHeader("x-api-key", apiKey)
                .build();
    }
}
