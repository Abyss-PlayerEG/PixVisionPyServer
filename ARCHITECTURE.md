# 项目架构说明

## 📁 目录结构

```
pix-version-py-server/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── main.py                   # FastAPI 主应用入口
│   │
│   ├── core/                     # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py             # 配置管理
│   │   └── exceptions.py         # 自定义异常
│   │
│   ├── routers/                  # 路由层（Controller）
│   │   ├── __init__.py
│   │   └── accounts.py           # 账号检测路由
│   │
│   ├── services/                 # 服务层（Service）
│   │   ├── __init__.py
│   │   ├── base_service.py       # 服务基类（抽象）
│   │   ├── bilibili_service.py   # B站服务实现
│   │   ├── douyin_service.py     # 抖音服务实现（示例）
│   │   └── service_factory.py    # 服务工厂
│   │
│   ├── schemas/                  # 数据模型层（DTO）
│   │   ├── __init__.py
│   │   ├── response.py           # 统一响应模型
│   │   └── bilibili.py           # B站用户模型
│   │
│   └── models/                   # 数据库模型层（预留）
│       └── __init__.py
│
├── .env                          # 环境变量配置
├── .env.example                  # 配置模板
├── pyproject.toml                # 项目依赖
├── README.md                     # 项目说明
└── ARCHITECTURE.md               # 架构说明（本文件）
```

## 🏗️ 架构设计

### 分层架构

本项目采用经典的三层架构：

1. **路由层 (Routers)** - 类似 MVC 的 Controller
   - 处理 HTTP 请求和响应
   - 参数验证
   - 调用服务层
   - 返回统一格式的响应

2. **服务层 (Services)** - 类似 MVC 的 Service
   - 业务逻辑实现
   - 第三方 API 调用
   - 数据处理
   - 使用策略模式支持多平台

3. **模型层 (Schemas/Models)** - 类似 MVC 的 Model
   - Pydantic 数据模型
   - 请求/响应数据结构定义
   - 数据验证

### 设计模式

#### 1. 策略模式 (Strategy Pattern)

每个平台的服务都继承自 `BaseAccountService`，实现统一的接口：

```python
class BaseAccountService(ABC):
    @abstractmethod
    async def check_account_exists(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def validate_user_id(self, user_id: str) -> bool:
        pass
```

#### 2. 工厂模式 (Factory Pattern)

`ServiceFactory` 根据平台名称动态创建对应的服务实例：

```python
service = ServiceFactory.get_service("bilibili")
```

#### 3. 开闭原则 (Open-Closed Principle)

- **对扩展开放**：添加新平台只需创建新的服务类并注册
- **对修改关闭**：无需修改现有代码

## 🔌 RESTful API 设计

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/accounts/{platform}/{user_id}` | 检测账号是否存在 |
| GET | `/api/v1/accounts/{platform}/{user_id}/info` | 获取账号详细信息 |
| GET | `/api/v1/accounts/platforms` | 获取支持的平台列表 |

### 统一响应格式

所有接口都返回统一的 JSON 格式：

**成功响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "platform": "bilibili",
    "user_id": "520500365",
    "exists": true
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

**错误响应：**
```json
{
  "code": 404,
  "message": "账号不存在",
  "error_detail": "B站用户 520500365 不存在",
  "timestamp": "2024-01-01T12:00:00"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误（平台不支持、ID格式错误等） |
| 404 | 账号不存在 |
| 502 | 第三方 API 请求失败 |
| 500 | 服务器内部错误 |

## 🚀 如何添加新平台

添加新平台非常简单，只需 3 步：

### 步骤 1: 创建服务类

在 `app/services/` 下创建新的服务文件，如 `weibo_service.py`：

```python
from typing import Dict, Any
from app.services.base_service import BaseAccountService


class WeiboService(BaseAccountService):
    """微博账号检测服务"""
    
    @property
    def platform_name(self) -> str:
        return "weibo"
    
    async def check_account_exists(self, user_id: str) -> bool:
        # 实现微博 API 调用逻辑
        pass
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        # 实现获取用户信息逻辑
        pass
    
    async def validate_user_id(self, user_id: str) -> bool:
        # 实现用户ID验证逻辑
        pass
```

### 步骤 2: 注册服务

在 `app/services/service_factory.py` 中注册新服务：

```python
_services: Dict[str, BaseAccountService] = {
    "bilibili": BilibiliService(),
    "douyin": DouyinService(),
    "weibo": WeiboService(),  # 添加这一行
}
```

### 步骤 3: 更新配置（可选）

在 `.env` 文件中更新支持的平台列表：

```bash
SUPPORTED_PLATFORMS=bilibili,douyin,weibo
```

**完成！** 无需修改任何其他代码，新平台立即可用。

## 📝 代码示例

### 检测账号是否存在

```bash
curl "http://localhost:8000/api/v1/accounts/bilibili/520500365"
```

### 获取账号详细信息

```bash
curl "http://localhost:8000/api/v1/accounts/bilibili/520500365/info"
```

### 获取支持的平台列表

```bash
curl "http://localhost:8000/api/v1/accounts/platforms"
```

## 🎯 优势总结

1. **模块化设计** - 清晰的职责分离
2. **易于扩展** - 添加新平台只需 3 步
3. **RESTful 规范** - 标准的 API 设计
4. **统一响应** - 一致的返回格式
5. **类型安全** - Pydantic 数据验证
6. **异步支持** - 高性能异步处理
7. **自动文档** - Swagger UI + ReDoc
8. **错误处理** - 统一的异常管理

## 🔧 技术栈

- **FastAPI** - Web 框架
- **Pydantic** - 数据验证
- **HTTPX** - 异步 HTTP 客户端
- **Uvicorn** - ASGI 服务器
- **uv** - 包管理器
