"""
应用配置模块
集中管理所有配置项
"""
import json
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional


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
    
    # B站 API 配置
    BILIBILI_API_BASE: str = "https://api.bilibili.com"
    BILIBILI_SESSDATA: str = ""  # B站认证 Cookie（从配置文件加载）
    
    # API 文档配置
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    
    # CORS 配置
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 从外部配置文件加载 BILIBILI_SESSDATA
        self._load_bilibili_config()
    
    def _load_bilibili_config(self):
        """从外部 JSON 配置文件加载 B站配置"""
        try:
            # 构建配置文件路径: ~/.pix_vision/python-server-conf.json
            home_dir = Path.home()
            config_file = home_dir / ".pix_vision" / "python-server-conf.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                    # 尝试从配置中获取 SESSDATA
                    # 支持多种可能的键名
                    sessdata = (
                        config_data.get('bilibili', {}).get('sessdata') or
                        config_data.get('bilibili', {}).get('SESSDATA') or
                        config_data.get('BILIBILI_SESSDATA') or
                        config_data.get('sessdata') or
                        config_data.get('SESSDATA') or
                        ""
                    )
                    
                    if sessdata:
                        self.BILIBILI_SESSDATA = sessdata
                        print(f"✅ 已从配置文件加载 BILIBILI_SESSDATA: {config_file}")
                    else:
                        print(f"⚠️  配置文件中未找到 SESSDATA: {config_file}")
            else:
                print(f"⚠️  配置文件不存在: {config_file}")
                print(f"   请创建文件并添加 B站 SESSDATA 配置")
                
        except Exception as e:
            print(f"❌ 加载 B站配置文件失败: {e}")


# 创建全局配置实例
settings = Settings()
