"""
B站账号检测服务
"""
import httpx
import asyncio
from typing import Dict, Any, Optional
from app.services.base_service import BaseAccountService
from app.core.exceptions import AccountNotFoundException, APIRequestException
from app.core.config import settings


class BilibiliService(BaseAccountService):
    """B站账号检测服务实现"""
    
    # B站 API 基础 URL
    API_BASE_URL = "https://api.bilibili.com"
    
    # 默认请求头
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    # 最大重试次数
    MAX_RETRIES = 3
    # 重试延迟（秒）
    RETRY_DELAY = 1
    
    # 限流重试配置
    RATE_LIMIT_MAX_RETRIES = 25  # 限流时最大重试次数
    RATE_LIMIT_RETRY_DELAY = 1   # 限流时每次重试间隔（秒）
    
    @property
    def platform_name(self) -> str:
        return "bilibili"
    
    async def _make_request(
        self, 
        url: str, 
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
        handle_rate_limit: bool = True
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求（带重试机制）
        
        Args:
            url: 请求 URL
            params: 查询参数
            headers: 请求头
            cookies: Cookie
            handle_rate_limit: 是否处理限流错误（code: -799）
            
        Returns:
            响应数据
            
        Raises:
            APIRequestException: 请求失败时抛出
        """
        last_exception = None
        
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                request_headers = {**self.DEFAULT_HEADERS, **(headers or {})}
                
                async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                    response = await client.get(
                        url, 
                        params=params,
                        headers=request_headers,
                        cookies=cookies
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # 检查是否为限流错误
                    if handle_rate_limit and data.get("code") == -799:
                        if attempt < self.MAX_RETRIES:
                            await asyncio.sleep(self.RETRY_DELAY)
                            continue
                        else:
                            # 达到最大重试次数，使用特殊的限流重试逻辑
                            return await self._handle_rate_limit(url, params, headers, cookies)
                    
                    return data
                    
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(self.RETRY_DELAY * attempt)  # 指数退避
                    continue
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise AccountNotFoundException(
                        platform=self.platform_name,
                        user_id=params.get("mid", "unknown") if params else "unknown",
                        message="账号不存在"
                    )
                last_exception = e
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(self.RETRY_DELAY)
                    continue
                    
            except Exception as e:
                last_exception = e
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(self.RETRY_DELAY)
                    continue
        
        # 所有重试都失败
        raise APIRequestException(
            self.platform_name,
            f"请求失败（已重试{self.MAX_RETRIES}次）: {str(last_exception)}"
        )
    
    async def _handle_rate_limit(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        处理限流错误（code: -799）
        每隔 1 秒重新请求，直到成功或达到最大重试次数
        
        Args:
            url: 请求 URL
            params: 查询参数
            headers: 请求头
            cookies: Cookie
            
        Returns:
            响应数据
            
        Raises:
            APIRequestException: 达到最大重试次数后仍然限流
        """
        last_data = None
        
        for attempt in range(1, self.RATE_LIMIT_MAX_RETRIES + 1):
            try:
                request_headers = {**self.DEFAULT_HEADERS, **(headers or {})}
                
                async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                    response = await client.get(
                        url,
                        params=params,
                        headers=request_headers,
                        cookies=cookies
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # 如果不再是限流错误，直接返回
                    if data.get("code") != -799:
                        return data
                    
                    last_data = data
                    
                    # 如果不是最后一次尝试，等待 1 秒后重试
                    if attempt < self.RATE_LIMIT_MAX_RETRIES:
                        await asyncio.sleep(self.RATE_LIMIT_RETRY_DELAY)
                        
            except Exception as e:
                # 网络错误等其他异常，继续重试
                if attempt < self.RATE_LIMIT_MAX_RETRIES:
                    await asyncio.sleep(self.RATE_LIMIT_RETRY_DELAY)
                    continue
                else:
                    raise APIRequestException(
                        self.platform_name,
                        f"请求失败（限流重试{attempt}次）: {str(e)}"
                    )
        
        # 达到最大重试次数，仍然限流
        raise APIRequestException(
            self.platform_name,
            f"请求过于频繁，已重试{self.RATE_LIMIT_MAX_RETRIES}次仍被限流",
            error_detail=last_data.get("message", "请求过于频繁") if last_data else "请求过于频繁"
        )
    
    async def check_account_exists(self, user_id: str) -> bool:
        """
        检查B站账号是否存在
        
        Args:
            user_id: B站用户ID (mid)
            
        Returns:
            账号是否存在
        """
        url = f"{self.API_BASE_URL}/x/space/acc/info"
        params = {"mid": user_id}
        
        try:
            data = await self._make_request(url, params=params)
            
            # code=0 表示成功，-404 表示用户不存在
            return data.get("code") == 0
                
        except AccountNotFoundException:
            return False
        except APIRequestException:
            raise
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取B站用户详细信息
        
        Args:
            user_id: B站用户ID (mid)
            
        Returns:
            用户信息字典
            
        Raises:
            AccountNotFoundException: 账号不存在时抛出
            APIRequestException: 请求失败时抛出
        """
        url = f"{self.API_BASE_URL}/x/space/acc/info"
        params = {"mid": user_id}
        
        data = await self._make_request(url, params=params)
        
        if data.get("code") == 0:
            return data.get("data", {})
        elif data.get("code") == -404:
            raise AccountNotFoundException(
                platform=self.platform_name,
                user_id=user_id,
                message=f"B站用户 {user_id} 不存在"
            )
        else:
            raise APIRequestException(
                self.platform_name,
                data.get("message", "未知错误")
            )
    
    async def validate_user_id(self, user_id: str) -> bool:
        """验证B站用户ID格式（应该是数字）"""
        try:
            int(user_id)
            return True
        except ValueError:
            return False
