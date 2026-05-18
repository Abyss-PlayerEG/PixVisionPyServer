"""
服务工厂
根据平台名称动态创建对应的服务实例
"""
from typing import Dict
from app.services.base_service import BaseAccountService
from app.services.bilibili_service import BilibiliService
from app.core.exceptions import PlatformNotSupportedException
from app.core.config import settings


class ServiceFactory:
    """
    服务工厂类
    
    使用工厂模式 + 策略模式，根据平台名称返回对应的服务实例
    """
    
    # 注册所有可用的服务
    _services: Dict[str, BaseAccountService] = {
        "bilibili": BilibiliService(),
    }
    
    @classmethod
    def get_service(cls, platform: str) -> BaseAccountService:
        """
        根据平台名称获取对应的服务实例
        
        Args:
            platform: 平台名称
            
        Returns:
            对应的服务实例
            
        Raises:
            PlatformNotSupportedException: 平台不支持时抛出
        """
        platform_lower = platform.lower()
        
        # 检查平台是否在支持的列表中
        if platform_lower not in cls._services:
            raise PlatformNotSupportedException(
                platform=platform_lower,
                supported_platforms=cls.get_supported_platforms()
            )
        
        return cls._services[platform_lower]
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """获取所有支持的平台列表"""
        return list(cls._services.keys())
    
    @classmethod
    def register_service(cls, platform: str, service: BaseAccountService):
        """
        注册新的平台服务（用于动态扩展）
        
        Args:
            platform: 平台名称
            service: 服务实例
        """
        cls._services[platform.lower()] = service
