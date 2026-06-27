# PixVision PyServer

**像素视觉 Python 辅助服务** — AI 审核与多平台账号检测

[![Python](https://img.shields.io/badge/Python-3.14+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-brightgreen)](https://fastapi.tiangolo.com/)
[![Version](https://img.shields.io/badge/Version-1.0.0-purple)]()

---

## 项目简介

PixVision PyServer 是基于 Python FastAPI 构建的辅助服务端，为 PixVision 主项目提供两大核心能力：

- **多平台账号检测**：支持 B 站等平台的账号存在性检测和用户信息查询
- **AI 文案内容审核**：基于大模型的智能内容审核，自动识别违规 / 中立 / 正常内容

所有接口遵循 RESTful API 设计规范，返回统一 JSON 响应格式，并自动生成交互式 API 文档（Swagger / ReDoc）。

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.14+ | 运行环境 |
| FastAPI | 0.136+ | 高性能异步 Web 框架 |
| Uvicorn | 0.47+ | ASGI 服务器 |
| Pydantic v2 | 2.x | 请求 / 响应模型校验 |
| httpx | 0.28+ | 异步 HTTP 客户端 |
| OpenAI SDK | 1.3+ | 兼容 OpenAI 协议的大模型调用 |

## 核心功能

### 账号检测

- 快速检测指定平台账号是否存在
- 获取用户完整信息（昵称、等级、头像等）
- 支持查看当前所支持的平台列表
- 统一错误处理和降级兜底

### AI 文案审核

- 黑名单前置过滤（2400+ 敏感词），命中秒回，不消耗 AI Token
- AI 模型深度审核，三态输出：`normal`（正常）/ `neutral`（存疑）/ `violation`（违规）
- 智能重试机制（最多 9 次），格式错误自动修正
- 失败优雅降级，不影响业务流程

## 快速开始

### 环境要求

- Python 3.14+
- 包管理器：`uv`（推荐）或 `pip`

### 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 配置外部服务

在用户目录 `~/.pix_vision/python-server-conf.json` 创建配置文件：

```json
{
  "ai": {
    "api_key": "your-api-key-here",
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com",
    "timeout": 10
  },
  "bilibili": {
    "SESSDATA": "your-bilibili-sessdata-here"
  }
}
```

| 配置项 | 必填 | 说明 |
|--------|------|------|
| ai.api_key | 是 | AI 服务 API Key |
| ai.model | 是 | 模型名称（如 deepseek-chat、gpt-4o） |
| ai.base_url | 否 | API 地址，为空则使用官方默认 |
| ai.timeout | 否 | 超时秒数，默认 3 |
| bilibili.SESSDATA | 否 | B 站 Cookie，用于获取用户信息 |

### 启动服务

```bash
uv run python -m app.main
```

默认监听 `0.0.0.0:8000`，启动后访问：

| 服务 | 地址 |
|------|------|
| 交互式 API 文档 | [http://localhost:8000/docs](http://localhost:8000/docs) |
| 备用文档（ReDoc） | [http://localhost:8000/redoc](http://localhost:8000/redoc) |
| 健康检查 | [http://localhost:8000/health](http://localhost:8000/health) |

## API 概览

### 账号检测

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/accounts/{platform}/{user_id}` | 检测账号是否存在 |
| `GET` | `/api/v1/accounts/{platform}/{user_id}/info` | 获取账号详细信息 |
| `GET` | `/api/v1/accounts/platforms` | 查看支持的平台列表 |

### AI 文案审核

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/content/audit` | 提交文案进行 AI 内容审核 |
| `GET` | `/api/v1/content/config` | 查询 AI 审核服务配置状态 |

### 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "timestamp": "2024-01-01T12:00:00"
}
```

- `code = 0` 表示成功，非 0 表示异常
- `data` 中包含实际返回数据

### 快速调用示例

```bash
# 检测 B 站账号
curl http://localhost:8000/api/v1/accounts/bilibili/520500365

# AI 文案审核
curl -X POST "http://localhost:8000/api/v1/content/audit" \
  -H "Content-Type: application/json" \
  -d '{"text": "今天天气真好，一起去公园玩吧。"}'
```

## 项目结构

```
PixVisionPyServer/
├── app/
│   ├── core/                # 核心模块
│   │   ├── config.py        # 应用配置
│   │   ├── exceptions.py    # 自定义异常
│   │   └── prompts/         # AI 提示词 & 敏感词库
│   ├── models/              # 数据模型
│   ├── routers/             # 路由层
│   │   ├── accounts.py      # 账号检测路由
│   │   └── ai_audit.py      # AI 审核路由
│   ├── schemas/             # Pydantic 数据校验
│   ├── services/            # 业务服务层
│   └── main.py              # 应用入口
├── doc/                     # 接口文档
├── pyproject.toml           # 项目元数据 & 依赖
└── python-server-conf.example.json  # 配置文件示例
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 404 | 用户不存在 |
| 500 | 服务器内部错误 |
| 502 | 上游 API 请求失败 |
| 503 | AI 服务未配置或不可用 |

## 扩展新平台

项目采用工厂模式设计，新增平台只需：

1. 继承 `BaseService` 并实现平台逻辑
2. 在 `ServiceFactory` 中注册

```python
from app.services.base_service import BaseService

class NewPlatformService(BaseService):
    async def check_account_exists(self, user_id: str) -> bool:
        ...

    async def get_user_info(self, user_id: str) -> dict:
        ...
```

## 相关项目

| 项目 | 说明 | 仓库 |
|------|------|------|
| **PixVisionPage** | Vue 3 前端应用 | [Gitee](https://gitee.com/endergaster_geek/PixVisionPage) |
| **PixVisionServer** | Java 后端服务（Spring Boot） | [Gitee](https://gitee.com/endergaster_geek/PixVisionServer) |

## 作者

- PlayerEG — gaster@vip.playereg.top

## 许可证

本项目基于 MIT 许可证开源。
