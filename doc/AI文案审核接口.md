# AI 文案审核接口

## 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/content/audit` | 提交文案进行 AI 内容安全审核 |
| GET | `/api/v1/content/config` | 查询 AI 审核服务配置状态 |

---

## 一、提交审核 `POST /api/v1/content/audit`

### 请求参数

**Content-Type**: `application/json`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 待审核文案，1-5000 字符 |

### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/content/audit" \
  -H "Content-Type: application/json" \
  -d '{"text": "今天天气真好，一起去公园玩吧。"}'
```

### 响应格式

统一响应结构：

```json
{
  "code": 0,
  "message": "审核完成",
  "data": {
    "status": "normal",
    "reason": "日常问候",
    "insult_words": []
  },
  "timestamp": "2026-05-22T12:00:00"
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 业务状态码，0 表示成功 |
| message | string | 响应消息 |
| data.status | string | 审核结果：`normal` / `neutral` / `violation` |
| data.reason | string | 判断依据简述 |
| data.insult_words | array | 命中敏感词数组 |
| timestamp | string | 响应时间戳 |

### 审核状态说明

| 状态 | 含义 | 示例场景 |
|------|------|----------|
| `normal` | 正常内容 | 日常问候、中性表达、常识问答 |
| `neutral` | 中立/存疑 | 轻度攻击性用词、低俗暗示、争议内容、审核服务异常降级 |
| `violation` | 违规内容 | 命中敏感词黑名单、色情暴力、仇恨言论、政治敏感等 |

---

## 二、审核流程

```
用户请求
  │
  ├─ ① 黑名单前置过滤（正则匹配 2400+ 敏感词）
  │   ├─ 命中 → 直接返回 violation（不调用 AI，秒级响应）
  │   └─ 未命中 ↓
  │
  ├─ ② AI 模型审核（deepseek / gpt 等）
  │   ├─ temperature=0.1 保证输出稳定
  │   ├─ 决策树：步骤1 violation → 步骤2 neutral → 步骤3 normal
  │   └─ 解析 JSON 响应，验证格式
  │       ├─ 格式正确 → 返回结果
  │       └─ 格式错误 → 重试（最多 9 次，附带修正提示）
  │
  └─ ③ 降级兜底
      └─ 全部重试失败 → 返回 neutral（人工复核）
```

**关键特性**：
- 黑名单前置过滤，命中秒回，节省 AI 调用成本
- 10 次尝试机会（1 初始 + 9 重试），保证可用性
- 失败优雅降级，不阻塞业务流程

---

## 三、完整调用示例

### 正常内容

```bash
curl -X POST "http://localhost:8000/api/v1/content/audit" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好，今天有什么好玩的游戏推荐吗？"}'
```

响应：
```json
{
  "code": 0,
  "message": "审核完成",
  "data": {
    "status": "normal",
    "reason": "日常问候",
    "insult_words": []
  }
}
```

### 违规内容（命中黑名单）

```bash
curl -X POST "http://localhost:8000/api/v1/content/audit" \
  -H "Content-Type: application/json" \
  -d '{"text": "你这个蠢货，死全家吧"}'
```

响应（秒回，不走 AI）：
```json
{
  "code": 0,
  "message": "审核完成",
  "data": {
    "status": "violation",
    "reason": "命中敏感词黑名单",
    "insult_words": ["蠢", "死全家"]
  }
}
```

### 中立内容（AI 判断）

```bash
curl -X POST "http://localhost:8000/api/v1/content/audit" \
  -H "Content-Type: application/json" \
  -d '{"text": "这个游戏感觉一般，有点问题"}'
```

响应：
```json
{
  "code": 0,
  "message": "审核完成",
  "data": {
    "status": "neutral",
    "reason": "待复核",
    "insult_words": []
  }
}
```

---

## 四、配置状态查询 `GET /api/v1/content/config`

### 请求示例

```bash
curl "http://localhost:8000/api/v1/content/config"
```

### 响应示例

```json
{
  "code": 0,
  "message": "配置状态查询成功",
  "data": {
    "configured": true,
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com",
    "timeout": 10
  }
}
```

---

## 五、错误码

| code | 说明 |
|------|------|
| 0 | 审核成功 |
| 400 | 请求参数错误（text 长度不符合 1-5000） |
| 503 | AI 服务未配置或不可用 |
| 500 | 服务器内部错误 |

---

## 六、配置说明

AI 审核需要在 `~/.pix_vision/python-server-conf.json` 中配置：

```json
{
  "ai": {
    "api_key": "your-api-key",
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com",
    "timeout": 10
  }
}
```

| 配置项 | 必填 | 说明 | 默认值 |
|--------|------|------|--------|
| api_key | 是 | AI 服务 API Key | - |
| model | 是 | 模型名称 | - |
| base_url | 否 | API 地址 | 官方默认 |
| timeout | 否 | 超时秒数 | 3 |

重试次数可通过环境变量或配置调整：`AI_AUDIT_MAX_RETRIES`（默认 9 次）。

---

## 七、接入建议

1. **先调配置接口**：启动后调用 `/config` 确认 AI 服务已正确配置
2. **合理设置超时**：根据模型响应速度调整 `timeout`，建议 10-30 秒
3. **处理 neutral**：neutral 可能是 AI 不确定或服务降级，建议走人工复核流程
4. **violation 即拦截**：violation 内容应直接拒绝发布
5. **黑名单优先**：命中黑名单的请求不会消耗 AI Token，可放心高频调用
