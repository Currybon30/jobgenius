package com.job_recommender_system.auth_server.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class FastAPICreateRequest {
    private Long uid;
}
