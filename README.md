# B站账号检测 API

使用 FastAPI 和 uv 构建的 B站账号检测服务，提供类似 Spring Boot Knife4j 的美观 API 文档。

## 🌟 特性亮点

### 📚 类似 Knife4j 的文档体验

- ✨ **Swagger UI** - 交互式 API 文档 (`/docs`)
- 📖 **ReDoc** - 更美观的文档界面 (`/redoc`)
- 🎨 **自定义主题** - 美化的文档展示
- 📝 **详细注释** - 完整的参数说明和示例
- 🏷️ **标签分组** - API 接口分类管理
- 🔍 **在线测试** - 直接在文档中测试 API

## 功能特性

- ✅ 检测 B站账号是否存在
- ✅ 获取用户详细信息（用户名、等级、签名等）
- ✅ 支持 SESSDATA Cookie 认证
- ✅ 提供完整和简化两种接口
- ✅ 自动生成的 API 文档

## 环境要求

- Python 3.14+
- uv 包管理器

## 安装

```bash
# 安装依赖
uv sync
```

## 运行

```bash
# 启动服务器
uv run python main.py
```

服务器将在 `http://0.0.0.0:8000` 上运行。

## API 接口

### 1. 首页
```
GET /
```
返回 API 基本信息和使用示例。

### 2. 检测用户（完整版）
```
GET /check_user?mid=520500365&sessdata=your_sessdata
```

**参数：**
- `mid` (必填): B站用户 ID
- `sessdata` (可选): B站登录凭证

**响应示例：**
```json
{
  "code": 0,
  "message": "用户存在",
  "data": {
    "mid": 520500365,
    "name": "用户名",
    "sex": "男",
    "face": "头像URL",
    "sign": "个性签名",
    "level": 6,
    "jointime": 0,
    "motto": "",
    "coins": null,
    "fans_badge": false
  }
}
```

### 3. 检测用户（简化版）
```
GET /check_user_simple?mid=520500365&sessdata=your_sessdata
```

**参数：**
- `mid` (必填): B站用户 ID
- `sessdata` (可选): B站登录凭证

**响应示例：**
```json
{
  "exists": true,
  "mid": 520500365,
  "name": "用户名"
}
```

## API 文档

启动服务器后，访问以下地址查看交互式 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 使用示例

### cURL

```bash
# 基础检测
curl "http://localhost:8000/check_user?mid=520500365"

# 带 Cookie 检测
curl "http://localhost:8000/check_user?mid=520500365&sessdata=your_sessdata_here"

# 简化版检测
curl "http://localhost:8000/check_user_simple?mid=520500365"
```

### Python

```python
import requests

# 检测用户
response = requests.get(
    "http://localhost:8000/check_user",
    params={"mid": 520500365}
)
print(response.json())
```

## 项目结构

```
pix-version-py-server/
├── main.py              # FastAPI 应用主文件
├── config.py            # 配置管理（类似 Spring Boot 的 application.yml）
├── middleware.py        # 中间件（类似 Spring Boot 的拦截器）
├── pyproject.toml       # 项目配置和依赖
├── uv.lock             # 依赖锁定文件
├── .env.example        # 环境变量示例文件
├── .venv/              # 虚拟环境
└── README.md           # 项目说明
```

## 技术栈

- **FastAPI**: 高性能 Web 框架
- **Uvicorn**: ASGI 服务器
- **HTTPX**: 异步 HTTP 客户端
- **Pydantic**: 数据验证和设置管理
- **uv**: 快速的 Python 包管理器

## 📖 API 文档（类似 Knife4j）

### 1. Swagger UI (推荐)
访问: http://localhost:8000/docs

特点：
- 🎯 交互式界面，可直接测试 API
- 📋 完整的参数说明和示例值
- 🔐 支持认证配置
- 💾 可导出 OpenAPI 规范

### 2. ReDoc
访问: http://localhost:8000/redoc

特点：
- 📖 更美观的三栏布局
- 🎨 现代化的设计风格
- 📱 响应式设计，支持移动端
- 🔍 强大的搜索功能

### 3. OpenAPI JSON
访问: http://localhost:8000/openapi.json

获取完整的 OpenAPI 3.0 规范，可用于生成客户端代码。

## 注意事项

1. B站 API 可能需要 Cookie 认证才能获取完整信息
2. 请遵守 B站 API 使用规范，不要频繁请求
3. SESSDATA 是敏感信息，请妥善保管

## License

MIT