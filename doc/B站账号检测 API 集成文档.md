# B站账号检测 API 集成文档（Spring Boot）

## 📋 概述

本文档介绍如何在 Spring Boot 项目中调用 PixVision（像素视觉 Python FastApi 辅助服务端）API 的 B站账号检测接口。

**API 基础信息**:
- **Base URL**: `http://localhost:8000/api/v1`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

---

## 🔌 接口列表

### 1. 检测 B站账号是否存在

**接口地址**: `GET /accounts/bilibili/{user_id}`

**功能说明**: 快速检测指定的 B站用户 ID 是否存在

#### 请求参数

| 参数名 | 类型 | 必填 | 位置 | 说明 | 示例 |
|--------|------|------|------|------|------|
| user_id | String | 是 | Path | B站用户 ID (mid) | 520500365 |

#### 响应格式

**成功响应** (HTTP 200):
```json
{
  "code": 0,
  "message": "账号存在",
  "data": {
    "platform": "bilibili",
    "user_id": "520500365",
    "exists": true
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

**账号不存在** (HTTP 200):
```json
{
  "code": 0,
  "message": "账号不存在",
  "data": {
    "platform": "bilibili",
    "user_id": "520500365",
    "exists": false
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "无效的 bilibili 用户ID格式",
  "error_detail": null,
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 业务状态码

| code | 说明 |
|------|------|
| 0 | 请求成功 |
| 400 | 参数错误（无效的用户 ID 格式或不支持的平台） |
| 502 | B站 API 请求失败（网络错误、限流等） |
| 500 | 服务器内部错误 |

---

### 2. 获取 B站用户详细信息

**接口地址**: `GET /accounts/bilibili/{user_id}/info`

**功能说明**: 获取指定 B站用户的完整信息

#### 请求参数

| 参数名 | 类型 | 必填 | 位置 | 说明 | 示例 |
|--------|------|------|------|------|------|
| user_id | String | 是 | Path | B站用户 ID (mid) | 520500365 |

#### 响应格式

**成功响应** (HTTP 200):
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "platform": "bilibili",
    "user_id": "520500365",
    "info": {
      "mid": 520500365,
      "name": "测试用户",
      "sex": "男",
      "face": "https://i0.hdslb.com/bfs/face/xxx.jpg",
      "sign": "这是我的签名",
      "level": 6,
      "jointime": 0,
      "motto": "",
      "birthday": "2000-01-01",
      "coins": 100,
      "fans_badge": false,
      "official": {
        "role": 0,
        "title": "",
        "desc": ""
      },
      "vip": {
        "type": 0,
        "status": 0
      }
    }
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

**用户不存在** (HTTP 200):
```json
{
  "code": 404,
  "message": "B站用户 520500365 不存在",
  "error_detail": null,
  "timestamp": "2024-01-01T12:00:00"
}
```

**限流错误** (HTTP 200):
```json
{
  "code": 502,
  "message": "bilibili API 请求失败: 请求过于频繁，已重试25次仍被限流",
  "error_detail": "请求过于频繁，请稍后再试",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 用户信息字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| mid | Integer | 用户 ID |
| name | String | 用户名 |
| sex | String | 性别（男/女/保密） |
| face | String | 头像 URL |
| sign | String | 个性签名 |
| level | Integer | 用户等级 (0-6) |
| jointime | Long | 注册时间戳 |
| motto | String | 座右铭 |
| birthday | String | 生日 |
| coins | Integer | 硬币数 |
| fans_badge | Boolean | 是否有粉丝勋章 |
| official | Object | 认证信息 |
| vip | Object | 会员信息 |

---

## 💻 Spring Boot 集成示例

### 1. 添加依赖

在 `pom.xml` 中添加 HTTP 客户端依赖（推荐使用 OkHttp 或 RestTemplate）：

```xml
<!-- 方式1: 使用 Spring Web (RestTemplate) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- 方式2: 使用 WebClient (响应式) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>

<!-- 方式3: 使用 OkHttp -->
<dependency>
    <groupId>com.squareup.okhttp3</groupId>
    <artifactId>okhttp</artifactId>
    <version>4.12.0</version>
</dependency>
```

### 2. 配置类

创建 API 配置类 `BilibiliApiConfig.java`:

```java
package com.example.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class BilibiliApiConfig {
    
    @Value("${bilibili.api.base-url:http://localhost:8000/api/v1}")
    private String baseUrl;
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
    
    public String getBaseUrl() {
        return baseUrl;
    }
}
```

在 `application.yml` 中配置：

```yaml
bilibili:
  api:
    base-url: http://localhost:8000/api/v1
```

### 3. 响应 DTO

创建统一响应类 `ApiResponse.java`:

```java
package com.example.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class ApiResponse<T> {
    private Integer code;
    private String message;
    private T data;
    private LocalDateTime timestamp;
    
    public boolean isSuccess() {
        return code != null && code == 0;
    }
}
```

创建账号检测结果类 `AccountCheckResult.java`:

```java
package com.example.dto;

import lombok.Data;

@Data
public class AccountCheckResult {
    private String platform;
    private String userId;
    private Boolean exists;
}
```

创建用户信息类 `BilibiliUserInfo.java`:

```java
package com.example.dto;

import lombok.Data;

@Data
public class BilibiliUserInfo {
    private Long mid;
    private String name;
    private String sex;
    private String face;
    private String sign;
    private Integer level;
    private Long jointime;
    private String motto;
    private String birthday;
    private Integer coins;
    private Boolean fansBadge;
    // 其他字段根据需要添加
}
```

创建用户详情结果类 `UserDetailResult.java`:

```java
package com.example.dto;

import lombok.Data;

@Data
public class UserDetailResult {
    private String platform;
    private String userId;
    private BilibiliUserInfo info;
}
```

### 4. 服务类

创建 B站 API 服务类 `BilibiliApiService.java`:

#### 方式1: 使用 RestTemplate

```java
package com.example.service;

import com.example.config.BilibiliApiConfig;
import com.example.dto.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

@Service
@RequiredArgsConstructor
@Slf4j
public class BilibiliApiService {
    
    private final RestTemplate restTemplate;
    private final BilibiliApiConfig apiConfig;
    
    /**
     * 检测 B站账号是否存在
     * 
     * @param userId B站用户 ID
     * @return 是否存在
     */
    public Boolean checkAccountExists(String userId) {
        try {
            String url = UriComponentsBuilder
                .fromUriString(apiConfig.getBaseUrl())
                .path("/accounts/bilibili/{userId}")
                .buildAndExpand(userId)
                .toUriString();
            
            log.info("调用 B站账号检测接口: {}", url);
            
            ResponseEntity<ApiResponse<AccountCheckResult>> response = 
                restTemplate.getForEntity(url, 
                    new ParameterizedTypeReference<ApiResponse<AccountCheckResult>>() {});
            
            ApiResponse<AccountCheckResult> apiResponse = response.getBody();
            
            if (apiResponse == null || !apiResponse.isSuccess()) {
                log.error("B站账号检测失败: {}", apiResponse != null ? apiResponse.getMessage() : "null");
                throw new RuntimeException("B站账号检测失败: " + 
                    (apiResponse != null ? apiResponse.getMessage() : "未知错误"));
            }
            
            AccountCheckResult result = apiResponse.getData();
            log.info("B站账号检测结果: userId={}, exists={}", result.getUserId(), result.getExists());
            
            return result.getExists();
            
        } catch (Exception e) {
            log.error("调用 B站 API 异常: userId={}, error={}", userId, e.getMessage(), e);
            throw new RuntimeException("调用 B站 API 失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 获取 B站用户详细信息
     * 
     * @param userId B站用户 ID
     * @return 用户信息
     */
    public BilibiliUserInfo getUserInfo(String userId) {
        try {
            String url = UriComponentsBuilder
                .fromUriString(apiConfig.getBaseUrl())
                .path("/accounts/bilibili/{userId}/info")
                .buildAndExpand(userId)
                .toUriString();
            
            log.info("调用 B站用户信息接口: {}", url);
            
            ResponseEntity<ApiResponse<UserDetailResult>> response = 
                restTemplate.getForEntity(url, 
                    new ParameterizedTypeReference<ApiResponse<UserDetailResult>>() {});
            
            ApiResponse<UserDetailResult> apiResponse = response.getBody();
            
            if (apiResponse == null || !apiResponse.isSuccess()) {
                log.error("获取 B站用户信息失败: {}", apiResponse != null ? apiResponse.getMessage() : "null");
                throw new RuntimeException("获取 B站用户信息失败: " + 
                    (apiResponse != null ? apiResponse.getMessage() : "未知错误"));
            }
            
            UserDetailResult result = apiResponse.getData();
            log.info("获取 B站用户信息成功: userId={}, name={}", 
                result.getUserId(), result.getInfo().getName());
            
            return result.getInfo();
            
        } catch (Exception e) {
            log.error("调用 B站 API 异常: userId={}, error={}", userId, e.getMessage(), e);
            throw new RuntimeException("调用 B站 API 失败: " + e.getMessage(), e);
        }
    }
}
```

#### 方式2: 使用 WebClient (推荐，支持异步)

```java
package com.example.service;

import com.example.config.BilibiliApiConfig;
import com.example.dto.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
@Slf4j
public class BilibiliApiServiceAsync {
    
    private final WebClient webClient;
    private final BilibiliApiConfig apiConfig;
    
    /**
     * 异步检测 B站账号是否存在
     */
    public Mono<Boolean> checkAccountExistsAsync(String userId) {
        return webClient.get()
            .uri(uriBuilder -> uriBuilder
                .path("/accounts/bilibili/{userId}")
                .build(userId))
            .retrieve()
            .bodyToMono(new ParameterizedTypeReference<ApiResponse<AccountCheckResult>>() {})
            .map(response -> {
                if (!response.isSuccess()) {
                    throw new RuntimeException("B站账号检测失败: " + response.getMessage());
                }
                return response.getData().getExists();
            })
            .doOnError(error -> log.error("调用 B站 API 异常: userId={}, error={}", userId, error.getMessage()));
    }
    
    /**
     * 异步获取 B站用户详细信息
     */
    public Mono<BilibiliUserInfo> getUserInfoAsync(String userId) {
        return webClient.get()
            .uri(uriBuilder -> uriBuilder
                .path("/accounts/bilibili/{userId}/info")
                .build(userId))
            .retrieve()
            .bodyToMono(new ParameterizedTypeReference<ApiResponse<UserDetailResult>>() {})
            .map(response -> {
                if (!response.isSuccess()) {
                    throw new RuntimeException("获取 B站用户信息失败: " + response.getMessage());
                }
                return response.getData().getInfo();
            })
            .doOnError(error -> log.error("调用 B站 API 异常: userId={}, error={}", userId, error.getMessage()));
    }
}
```

配置 WebClient Bean:

```java
@Bean
public WebClient webClient(BilibiliApiConfig apiConfig) {
    return WebClient.builder()
        .baseUrl(apiConfig.getBaseUrl())
        .build();
}
```

### 5. 控制器示例

创建测试控制器 `BilibiliController.java`:

```java
package com.example.controller;

import com.example.dto.BilibiliUserInfo;
import com.example.service.BilibiliApiService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/bilibili")
@RequiredArgsConstructor
public class BilibiliController {
    
    private final BilibiliApiService bilibiliApiService;
    
    /**
     * 检测 B站账号是否存在
     */
    @GetMapping("/check/{userId}")
    public ResponseEntity<Boolean> checkAccount(@PathVariable String userId) {
        Boolean exists = bilibiliApiService.checkAccountExists(userId);
        return ResponseEntity.ok(exists);
    }
    
    /**
     * 获取 B站用户详细信息
     */
    @GetMapping("/user/{userId}")
    public ResponseEntity<BilibiliUserInfo> getUserInfo(@PathVariable String userId) {
        BilibiliUserInfo userInfo = bilibiliApiService.getUserInfo(userId);
        return ResponseEntity.ok(userInfo);
    }
}
```

### 6. 使用示例

```java
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final BilibiliApiService bilibiliApiService;
    
    public void processUser(String userId) {
        // 1. 检测账号是否存在
        Boolean exists = bilibiliApiService.checkAccountExists(userId);
        
        if (exists) {
            // 2. 获取用户详细信息
            BilibiliUserInfo userInfo = bilibiliApiService.getUserInfo(userId);
            
            System.out.println("用户名: " + userInfo.getName());
            System.out.println("等级: " + userInfo.getLevel());
            System.out.println("签名: " + userInfo.getSign());
        } else {
            System.out.println("用户不存在");
        }
    }
}
```

---

## ⚠️ 注意事项

### 1. 超时配置

建议设置合理的超时时间：

```java
@Bean
public RestTemplate restTemplate() {
    SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
    factory.setConnectTimeout(5000);  // 连接超时 5 秒
    factory.setReadTimeout(15000);    // 读取超时 15 秒（考虑限流重试）
    return new RestTemplate(factory);
}
```

### 2. 限流处理

API 已内置限流重试机制（最多 25 次，每次间隔 1 秒），但建议在调用方也添加：

- **重试策略**: 遇到 502 错误时可适当重试
- **熔断保护**: 使用 Hystrix 或 Resilience4j 防止雪崩
- **缓存机制**: 对频繁查询的用户 ID 进行缓存

### 3. 并发控制

高频调用时建议：
- 使用线程池限制并发数
- 添加请求队列
- 实现本地速率限制

```java
@Bean
public ExecutorService executorService() {
    return Executors.newFixedThreadPool(10);
}
```

### 4. 错误处理

建议统一处理 API 错误：

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<String> handleRuntimeException(RuntimeException e) {
        log.error("API 调用异常", e);
        return ResponseEntity.status(500).body("服务暂时不可用，请稍后重试");
    }
}
```

### 5. 日志记录

建议记录关键日志：

```java
log.info("调用 B站 API: userId={}, api={}", userId, apiName);
log.debug("B站 API 响应: {}", response);
log.warn("B站 API 限流: userId={}, retryCount={}", userId, retryCount);
log.error("B站 API 失败: userId={}, error={}", userId, errorMessage);
```

---

## 🔍 调试技巧

### 1. 测试连通性

```bash
curl http://localhost:8000/api/v1/accounts/bilibili/520500365
```

### 2. 查看 API 文档

访问 Swagger UI: `http://localhost:8000/docs`

### 3. 启用详细日志

在 `application.yml` 中配置：

```yaml
logging:
  level:
    com.example.service.BilibiliApiService: DEBUG
    org.springframework.web.client.RestTemplate: DEBUG
```

---

## 📞 技术支持

如有问题，请检查：
1. API 服务是否正常运行
2. 网络连接是否正常
3. 用户 ID 格式是否正确（纯数字）
4. 查看 API 返回的错误信息

---

## 📝 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| DEV-1.0.0 | 2024-01-01 | 初始版本，提供账号检测和用户信息查询接口 |

---

**文档生成时间**: 2024-01-01  
**API 版本**: DEV-1.0.0
