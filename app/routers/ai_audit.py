"""
AI 文案审核路由模块
提供 AI 内容审核 API 接口
"""
from fastapi import APIRouter, HTTPException
from app.services.ai_audit_service import AIAuditService
from app.schemas.audit import AuditRequest, AuditResponse
from app.schemas.response import success_response, error_response
from app.core.config import settings


# 创建路由器
router = APIRouter(
    prefix="/content",
    tags=["AI 文案审核"],
    responses={
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"},
        503: {"description": "AI 服务不可用"}
    }
)

# 模块级单例：避免每次请求重复创建 OpenAI 客户端
_audit_service: AIAuditService | None = None


def get_audit_service() -> AIAuditService:
    """懒加载获取审核服务单例"""
    global _audit_service
    if _audit_service is None:
        _audit_service = AIAuditService()
    return _audit_service


@router.post("/audit", summary="AI 文案内容审核")
async def audit_content(request: AuditRequest):
    """
    AI 文案内容审核接口
    
    对用户输入的文案进行自动化内容审核，输出三种状态：
    - **normal**: 正常内容
    - **neutral**: 中立/存疑内容
    - **violation**: 违规内容
    
    - **text**: 待审核的文案内容（1-5000 字符）
    """
    # 检查 AI 配置
    if not settings.AI_API_KEY or not settings.AI_MODEL:
        return error_response(
            code=503,
            message="AI 服务未配置，请在 python-server-conf.json 中配置 AI 相关参数"
        )
    
    try:
        # 获取审核服务单例
        audit_service = get_audit_service()
        
        # 执行审核
        result = await audit_service.audit_text(request.text)
        
        return success_response(
            data={
                "status": result.status.value,
                "reason": result.reason,
                "insult_words": result.insult_words
            },
            message="审核完成"
        )
        
    except ValueError as e:
        # 配置错误
        return error_response(code=503, message=str(e))
    except Exception as e:
        # 其他错误
        return error_response(
            code=500,
            message="审核失败",
            error_detail=str(e)
        )


@router.get("/config", summary="获取 AI 审核配置状态")
async def get_ai_config_status():
    """
    获取 AI 审核服务的配置状态
    用于检查 AI 服务是否正确配置
    """
    is_configured = bool(settings.AI_API_KEY and settings.AI_MODEL)
    
    return success_response(
        data={
            "configured": is_configured,
            "model": settings.AI_MODEL if is_configured else None,
            "base_url": settings.AI_BASE_URL if is_configured else None,
            "timeout": settings.AI_AUDIT_TIMEOUT if is_configured else None
        },
        message="配置状态查询成功"
    )
