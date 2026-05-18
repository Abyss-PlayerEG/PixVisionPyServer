"""
应用配置模块
集中管理所有配置项
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    APP_NAME: str = "像素视觉 Python 辅助服务 API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "用于辅助像素视觉的 Python 辅助服务"
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 请求配置
    REQUEST_TIMEOUT: int = 10
    
    # API 文档配置
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    
    # CORS 配置
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
