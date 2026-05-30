"""
应用配置模块
集中管理所有配置项
"""
import json
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional, ClassVar


class Settings(BaseSettings):
    """应用配置类"""
    
    # 类变量（不是模型字段）
    home_dir: ClassVar[Path] = Path.home()
    config_file: ClassVar[Path] = home_dir / ".pix_vision" / "python-server-conf.json"

    # 应用基本信息
    APP_NAME: str = "像素视觉 - 辅助服务"
    APP_VERSION: str = "DEV-1.0.0"
    APP_DESCRIPTION: str = "像素视觉 - 辅助服务"
    
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
    ALLOWED_ORIGINS: List[str] = [
        "http://124.221.107.68:1899/",
        "http://127.0.0.1:1899/",
        "http://localhost:9090/",
    ]
    
    # AI 配置
    AI_API_KEY: str = ""
    AI_MODEL: str = ""
    AI_BASE_URL: Optional[str] = None
    AI_AUDIT_TIMEOUT: int = 10  # AI 审核超时时间（秒）
    AI_AUDIT_MAX_RETRIES: int = 9  # AI 审核最大重试次数
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 从外部配置文件加载配置
        self._load_bilibili_config()
        self._load_ai_config()
    
    def _load_bilibili_config(self):
        """从外部 JSON 配置文件加载 B站配置"""
        try:
            file:Path = Settings.config_file
            if file.exists():
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 尝试从配置中获取 SESSDATA
                    # 支持多种可能的键名
                    sessdata = (
                        data.get('', {}).get('sessdata') or
                        data.get('bilibili', {}).get('SESSDATA') or
                        data.get('BILIBILI_SESSDATA') or
                        data.get('sessdata') or
                        data.get('SESSDATA') or
                        ""
                    )
                    
                    if sessdata:
                        self.BILIBILI_SESSDATA = sessdata
                        print(f"✅ 已从配置文件加载 BILIBILI_SESSDATA: {file}")
                    else:
                        print(f"⚠️  配置文件中未找到 SESSDATA: {file}")
            else:
                print(f"⚠️  配置文件不存在: {file}")
                print(f"   请创建文件并添加 B站 SESSDATA 配置")
                
        except Exception as e:
            print(f"❌ 加载 B站配置文件失败: {e}")
    
    def _load_ai_config(self):
        """从外部 JSON 配置文件加载 AI 配置"""
        try:
            file:Path = Settings.config_file
            if file.exists():
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 尝试从配置中获取 AI 配置
                    # 支持多种可能的键名结构
                    ai_config = (
                        data.get('ai', {}) or
                        data.get('AI', {}) or
                        data.get('openai', {}) or
                        data.get('OPENAI', {})
                    )
                    
                    # 获取 API Key
                    api_key = (
                        ai_config.get('api_key') or
                        ai_config.get('API_KEY') or
                        ai_config.get('apikey') or
                        ai_config.get('APIKEY') or
                        data.get('AI_API_KEY') or
                        data.get('ai_api_key') or
                        ""
                    )
                    
                    # 获取 Model
                    model = (
                        ai_config.get('model') or
                        ai_config.get('MODEL') or
                        ai_config.get('model_name') or
                        ai_config.get('MODEL_NAME') or
                        data.get('AI_MODEL') or
                        data.get('ai_model') or
                        ""
                    )
                    
                    # 获取 Base URL（可选）
                    base_url = (
                        ai_config.get('base_url') or
                        ai_config.get('BASE_URL') or
                        ai_config.get('api_base') or
                        ai_config.get('API_BASE') or
                        data.get('AI_BASE_URL') or
                        data.get('ai_base_url') or
                        None
                    )
                    
                    # 获取超时时间（可选）
                    timeout = (
                        ai_config.get('timeout') or
                        ai_config.get('TIMEOUT') or
                        ai_config.get('audit_timeout') or
                        ai_config.get('AUDIT_TIMEOUT') or
                        3
                    )
                    
                    if api_key and model:
                        self.AI_API_KEY = api_key
                        self.AI_MODEL = model
                        self.AI_BASE_URL = base_url
                        self.AI_AUDIT_TIMEOUT = int(timeout)
                        print(f"✅ 已从配置文件加载 AI 配置: model={model}")
                    else:
                        print(f"⚠️  配置文件中未找到完整的 AI 配置 (需要 api_key 和 model): {file}")
            else:
                print(f"⚠️  配置文件不存在: {file}")
                print(f"   请创建文件并添加 AI 配置")
                
        except Exception as e:
            print(f"❌ 加载 AI 配置文件失败: {e}")


# 创建全局配置实例
settings = Settings()
