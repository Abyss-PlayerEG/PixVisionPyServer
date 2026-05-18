"""
B站用户数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class BilibiliUserInfo(BaseModel):
    """B站用户信息模型"""
    mid: int = Field(..., description="用户ID", json_schema_extra={"example": 520500365})
    name: str = Field(..., description="用户名", json_schema_extra={"example": "测试用户"})
    sex: str = Field(..., description="性别", json_schema_extra={"example": "男"})
    face: str = Field(..., description="头像URL", json_schema_extra={"example": "https://i0.hdslb.com/bfs/face/xxx.jpg"})
    sign: str = Field(..., description="个性签名", json_schema_extra={"example": "这是我的签名"})
    level: int = Field(..., description="用户等级", json_schema_extra={"example": 6})
    jointime: int = Field(..., description="注册时间戳", json_schema_extra={"example": 0})
    motto: str = Field(..., description="座右铭", json_schema_extra={"example": ""})
    coins: Optional[int] = Field(None, description="硬币数（需要登录）", json_schema_extra={"example": 100})
    fans_badge: bool = Field(False, description="是否有粉丝勋章", json_schema_extra={"example": False})
    
    class Config:
        json_schema_extra = {
            "title": "B站用户信息",
            "description": "B站账号的详细信息"
        }
