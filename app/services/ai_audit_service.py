"""
AI 文案审核服务
"""
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI, AsyncOpenAI
from app.core.config import settings
from app.core.prompts import load_ai_audit_prompt
from app.schemas.audit import AuditStatus, AuditResponse

# 配置日志
logger = logging.getLogger(__name__)


class AIAuditService:
    """AI 文案审核服务"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        if not settings.AI_API_KEY or not settings.AI_MODEL:
            raise ValueError("AI 配置不完整，请检查 python-server-conf.json 中的 AI 配置")
        
        # 加载系统提示词
        self.system_prompt = load_ai_audit_prompt()
        
        # 创建同步和异步客户端
        self.client = OpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        
        self.async_client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        
        self.model = settings.AI_MODEL
    
    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """
        解析 AI 返回的 JSON 响应
        
        Args:
            content: AI 返回的文本内容
            
        Returns:
            解析后的字典
            
        Raises:
            ValueError: 解析失败时抛出
        """
        try:
            # 尝试直接解析 JSON
            result = json.loads(content)
            
            # 验证必需字段
            if "status" not in result:
                raise ValueError("AI 响应缺少 'status' 字段")
            
            if "reason" not in result:
                raise ValueError("AI 响应缺少 'reason' 字段")
            
            # 验证 status 值
            if result["status"] not in ["normal", "neutral", "violation"]:
                raise ValueError(f"无效的 status 值: {result['status']}")
            
            # 确保 insult_words 字段存在
            if "insult_words" not in result:
                result["insult_words"] = []
            
            # 验证 insult_words 是数组
            if not isinstance(result["insult_words"], list):
                result["insult_words"] = []
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"AI 返回的不是有效的 JSON 格式") from e
    
    def _build_retry_message(self, attempt: int, error_detail: str) -> str:
        """
        构建重试时的格式修正提示
        
        Args:
            attempt: 当前重试次数
            error_detail: 上一次失败的详细原因
            
        Returns:
            追加到用户消息中的格式修正提示
        """
        max_retries = settings.AI_AUDIT_MAX_RETRIES
        return (
            f"\n\n[格式修正提示] 你上一次的输出不符合要求的 JSON 格式，错误原因：{error_detail}。"
            f"请严格只输出以下格式的 JSON，不要包含任何解释、标记或额外内容：\n"
            f'{{"status": "normal|neutral|violation", "reason": "判断依据", "insult_words": ["词1", "词2"]}}\n'
            f"这是第 {attempt}/{max_retries} 次重试。"
        )
    
    def _call_ai_sync(self, text: str, retry_message: str = "") -> dict:
        """
        单次 AI API 同步调用并解析结果
        
        Args:
            text: 待审核文案
            retry_message: 重试时的格式修正提示（首次调用为空）
            
        Returns:
            解析后的结果字典
            
        Raises:
            ValueError: 解析失败时抛出
        """
        user_content = f"请审核以下文案：\n{text}{retry_message}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=200,
            temperature=0.1,
            timeout=settings.AI_AUDIT_TIMEOUT
        )
        content = response.choices[0].message.content.strip()
        return self._parse_ai_response(content)
    
    async def _call_ai_async(self, text: str, retry_message: str = "") -> dict:
        """
        单次 AI API 异步调用并解析结果
        
        Args:
            text: 待审核文案
            retry_message: 重试时的格式修正提示（首次调用为空）
            
        Returns:
            解析后的结果字典
            
        Raises:
            ValueError: 解析失败时抛出
        """
        user_content = f"请审核以下文案：\n{text}{retry_message}"
        response = await self.async_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=200,
            temperature=0.1,
            timeout=settings.AI_AUDIT_TIMEOUT
        )
        content = response.choices[0].message.content.strip()
        return self._parse_ai_response(content)
    
    def audit_text_sync(self, text: str) -> AuditResponse:
        """
        同步审核文案内容（含重试机制）
        
        最多重试 N 次，直至 AI 返回正确格式的 JSON。
        全部失败后降级返回 neutral 状态。
        
        Args:
            text: 待审核的文案
            
        Returns:
            审核结果
        """
        max_retries = settings.AI_AUDIT_MAX_RETRIES
        retry_message = ""
        last_error = None
        
        for attempt in range(1, max_retries + 2):  # 首次 + N 次重试
            try:
                result = self._call_ai_sync(text, retry_message)
                
                response = AuditResponse(
                    status=AuditStatus(result["status"]),
                    reason=result["reason"],
                    insult_words=result.get("insult_words", []),
                    confidence=None
                )
                
                if attempt > 1:
                    logger.info(f"AI 审核在第 {attempt} 次尝试后成功")
                return response
                
            except ValueError as e:
                # 格式解析失败 - 构建修正提示并重试
                last_error = e
                if attempt <= max_retries:
                    logger.warning(f"AI 审核第 {attempt}/{max_retries+1} 次解析失败: {e}")
                    retry_message = self._build_retry_message(attempt + 1, str(e)[:100])
                else:
                    logger.error(f"AI 审核已达最大重试次数 {max_retries}，最后错误: {e}")
                    
            except Exception as e:
                # 网络/API 异常 - 直接重试
                last_error = e
                if attempt <= max_retries:
                    logger.warning(f"AI 审核第 {attempt}/{max_retries+1} 次 API 调用失败: {e}")
                else:
                    logger.error(f"AI 审核已达最大重试次数 {max_retries}，最后错误: {e}")
        
        # 所有重试均失败 - 降级返回 neutral
        logger.error(f"AI 文案审核重试 {max_retries} 次后仍然失败，降级返回中立状态")
        return AuditResponse(
            status=AuditStatus.NEUTRAL,
            reason=f"审核服务异常，已重试{max_retries}次后降级: {str(last_error)[:50] if last_error else '未知错误'}"
        )
    
    async def audit_text(self, text: str) -> AuditResponse:
        """
        异步审核文案内容（含重试机制）
        
        最多重试 N 次，直至 AI 返回正确格式的 JSON。
        全部失败后降级返回 neutral 状态。
        
        Args:
            text: 待审核的文案
            
        Returns:
            审核结果
        """
        max_retries = settings.AI_AUDIT_MAX_RETRIES
        retry_message = ""
        last_error = None
        
        for attempt in range(1, max_retries + 2):  # 首次 + N 次重试
            try:
                result = await self._call_ai_async(text, retry_message)
                
                response = AuditResponse(
                    status=AuditStatus(result["status"]),
                    reason=result["reason"],
                    insult_words=result.get("insult_words", []),
                    confidence=None
                )
                
                if attempt > 1:
                    logger.info(f"AI 异步审核在第 {attempt} 次尝试后成功")
                return response
                
            except ValueError as e:
                # 格式解析失败 - 构建修正提示并重试
                last_error = e
                if attempt <= max_retries:
                    logger.warning(f"AI 异步审核第 {attempt}/{max_retries+1} 次解析失败: {e}")
                    retry_message = self._build_retry_message(attempt + 1, str(e)[:100])
                else:
                    logger.error(f"AI 异步审核已达最大重试次数 {max_retries}，最后错误: {e}")
                    
            except Exception as e:
                # 网络/API 异常 - 直接重试
                last_error = e
                if attempt <= max_retries:
                    logger.warning(f"AI 异步审核第 {attempt}/{max_retries+1} 次 API 调用失败: {e}")
                else:
                    logger.error(f"AI 异步审核已达最大重试次数 {max_retries}，最后错误: {e}")
        
        # 所有重试均失败 - 降级返回 neutral
        logger.error(f"AI 异步文案审核重试 {max_retries} 次后仍然失败，降级返回中立状态")
        return AuditResponse(
            status=AuditStatus.NEUTRAL,
            reason=f"审核服务异常，已重试{max_retries}次后降级: {str(last_error)[:50] if last_error else '未知错误'}"
        )
