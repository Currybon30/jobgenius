package com.jobgenius.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class UserResponseAdmin {
    private Long uid;
    private String name;
    private String email;
    private String role;
    private String provider;
    private boolean fastAPISync;
}
