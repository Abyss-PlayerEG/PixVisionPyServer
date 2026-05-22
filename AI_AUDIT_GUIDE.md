# AI 文案智能审核功能使用指南

## 功能概述

AI 文案智能审核功能可以对用户输入的文案进行自动化内容审核，输出三种状态：
- **normal（正常）**: 内容符合法律法规及公序良俗，无任何风险
- **neutral（中立）**: 无明显违规，但存在擦边、争议观点、广告软文等需人工进一步判断
- **violation（违规）**: 明确包含色情、暴力、仇恨言论、政治敏感、诈骗等违法或严重不良信息

## 配置步骤

### 1. 创建配置文件

在用户目录下创建配置文件 `~/.pix_vision/python-server-conf.json`：

```bash
mkdir -p ~/.pix_vision
cp python-server-conf.example.json ~/.pix_vision/python-server-conf.json
```

### 2. 编辑配置文件

打开配置文件并填入你的 AI 服务信息：

```json
{
  "ai": {
    "api_key": "你的API密钥",
    "model": "gpt-4o",
    "base_url": null,
    "timeout": 3
  },
  "bilibili": {
    "SESSDATA": "你的B站SESSDATA"
  }
}
```

### 3. 配置说明

#### AI 配置项

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `api_key` | string | 是 | AI 服务的 API 密钥 | `sk-xxx` |
| `model` | string | 是 | 使用的模型名称 | `gpt-4o`, `gpt-3.5-turbo` |
| `base_url` | string/null | 否 | API 基础 URL（第三方服务需要） | `https://api.openai.com` |
| `timeout` | number | 否 | 审核超时时间（秒），默认 3 | `3` |

#### 支持的 AI 服务

1. **OpenAI 官方**
   ```json
   {
     "api_key": "sk-xxx",
     "model": "gpt-4o"
   }
   ```

2. **兼容 OpenAI 接口的第三方服务**（如 DeepSeek、智谱等）
   ```json
   {
     "api_key": "your-api-key",
     "model": "deepseek-chat",
     "base_url": "https://api.deepseek.com"
   }
   ```

## API 接口

### 1. 审核文案内容

**接口**: `POST /api/v1/content/audit`

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/content/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "今天天气真好，一起去公园玩吧。"
  }'
```

**响应示例**:
```json
{
  "code": 0,
  "message": "审核完成",
  "data": {
    "status": "normal",
    "reason": "内容为日常积极描述，无违规迹象",
    "confidence": null
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. 查看 AI 配置状态

**接口**: `GET /api/v1/content/config`

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/content/config"
```

**响应示例**:
```json
{
  "code": 0,
  "message": "配置状态查询成功",
  "data": {
    "configured": true,
    "model": "gpt-4o",
    "base_url": null,
    "timeout": 3
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

## 测试功能

启动服务后，运行测试脚本：

```bash
# 启动服务
uv run uvicorn app.main:app --reload

# 在另一个终端运行测试
python test/test_ai_audit.py
```

## Python 代码调用示例

```python
import requests

# 审核文案
response = requests.post(
    "http://localhost:8000/api/v1/content/audit",
    json={
        "text": "这是需要审核的文案内容"
    }
)

result = response.json()
print(f"审核结果: {result['data']['status']}")
print(f"原因: {result['data']['reason']}")
```

## 错误处理

| 场景 | 状态码 | 说明 |
|------|--------|------|
| AI 服务未配置 | 503 | 需要在配置文件中添加 AI 配置 |
| 文案为空 | 400 | 文案长度必须在 1-5000 字符之间 |
| AI 调用超时 | 200 | 降级返回 neutral 状态 |
| AI 返回格式错误 | 200 | 降级返回 neutral 状态 |

## 设计特性

1. **异步处理**: 使用异步 AI 客户端，不影响其他请求
2. **降级策略**: AI 服务异常时自动返回 neutral 状态
3. **超时控制**: 默认 3 秒超时，可在配置中调整
4. **日志记录**: 详细记录审核过程和错误信息
5. **灵活配置**: 支持多种 AI 服务提供商

## 常见问题

### Q: 支持哪些 AI 模型？
A: 支持所有兼容 OpenAI 接口的模型，包括 GPT-4、GPT-3.5、DeepSeek 等。

### Q: 如何切换不同的 AI 服务？
A: 修改配置文件中的 `api_key`、`model` 和 `base_url` 即可。

### Q: 审核速度慢怎么办？
A: 可以增加 `timeout` 值，或选择响应更快的模型（如 gpt-3.5-turbo）。

### Q: 配置文件必须放在 ~/.pix_vision/ 吗？
A: 是的，系统会自动从该路径读取配置文件。
