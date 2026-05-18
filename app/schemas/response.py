"""
统一响应模型
所有 API 返回都使用这个格式，符合 RESTful 规范
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class APIResponse(BaseModel):
    """
    统一 API 响应模型
    
    遵循 RESTful API 设计规范：
    - code: 业务状态码（0表示成功）
    - message: 响应消息
    - data: 响应数据
    - timestamp: 时间戳
    """
    code: int = Field(..., description="业务状态码，0表示成功", examples=[0])
    message: str = Field(..., description="响应消息", examples=["success"])
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="响应时间戳",
        examples=["2024-01-01T12:00:00"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "success",
                "data": {},
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int = Field(..., description="错误码", examples=[404])
    message: str = Field(..., description="错误消息", examples=["账号不存在"])
    error_detail: Optional[str] = Field(None, description="详细错误信息")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="错误发生时间"
    )


def success_response(data: Any = None, message: str = "success") -> dict:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        
    Returns:
        标准成功响应字典
    """
    return {
        "code": 0,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


def error_response(code: int, message: str, error_detail: str = None) -> dict:
    """
    创建错误响应
    
    Args:
        code: 错误码
        message: 错误消息
        error_detail: 详细错误信息
        
    Returns:
        标准错误响应字典
    """
    return {
        "code": code,
        "message": message,
        "error_detail": error_detail,
        "timestamp": datetime.now().isoformat()
    }
