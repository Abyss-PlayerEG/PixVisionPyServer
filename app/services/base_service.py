"""
账号检测服务基类
所有平台的服务都应该继承这个基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAccountService(ABC):
    """
    账号检测服务抽象基类
    
    使用策略模式，每个平台实现自己的服务类
    """
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """返回平台名称"""
        pass
    
    @abstractmethod
    async def check_account_exists(self, user_id: str, **kwargs) -> bool:
        """
        检查账号是否存在
        
        Args:
            user_id: 用户ID
            **kwargs: 其他参数（如 sessdata 等）
            
        Returns:
            账号是否存在
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        获取用户详细信息
        
        Args:
            user_id: 用户ID
            **kwargs: 其他参数（如 sessdata 等）
            
        Returns:
            用户信息字典
            
        Raises:
            AccountNotFoundException: 账号不存在时抛出
        """
        pass
    
    @abstractmethod
    async def validate_user_id(self, user_id: str) -> bool:
        """
        验证用户ID格式是否有效
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户ID是否有效
        """
        pass
