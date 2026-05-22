"""
AI 文案审核相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class AuditStatus(str, Enum):
    """审核状态枚举"""
    NORMAL = "normal"  # 正常
    NEUTRAL = "neutral"  # 中立
    VIOLATION = "violation"  # 违规


class AuditRequest(BaseModel):
    """AI 文案审核请求模型"""
    text: str = Field(
        ...,
        description="待审核的文案内容",
        min_length=1,
        max_length=5000,
        examples=["今天天气真好，一起去公园玩吧。"]
    )


class AuditResponse(BaseModel):
    """AI 文案审核响应模型"""
    status: AuditStatus = Field(
        ...,
        description="审核结果：normal(正常) / neutral(中立) / violation(违规)",
        examples=["normal"]
    )
    reason: str = Field(
        ...,
        description="判断依据简述（30字以内）",
        max_length=100,
        examples=["内容为日常积极描述，无违规迹象"]
    )
    insult_words: list[str] = Field(
        default_factory=list,
        description="文案中的侮辱性词汇数组",
        examples=[["有病", "唐完了"]]
    )
    confidence: Optional[float] = Field(
        None,
        description="置信度 0-1（可选）",
        ge=0.0,
        le=1.0,
        examples=[0.98]
    )
