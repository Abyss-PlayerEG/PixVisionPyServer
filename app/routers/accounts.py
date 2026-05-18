"""
账号检测路由模块
提供 RESTful API 接口
"""
from fastapi import APIRouter, HTTPException, Path
from app.services.service_factory import ServiceFactory
from app.schemas.response import success_response, error_response
from app.core.exceptions import (
    AccountNotFoundException, 
    PlatformNotSupportedException,
    APIRequestException,
    InvalidParameterException
)
from app.core.config import settings


# 创建路由器，使用版本前缀
router = APIRouter(
    prefix="/accounts",
    tags=["账号检测"],
    responses={
        404: {"description": "账号不存在"},
        400: {"description": "无效的平台或参数"},
        500: {"description": "服务器内部错误"}
    }
)


@router.get("/{platform}/{user_id}", summary="检测指定平台的账号")
async def check_account(
    platform: str = Path(..., description="平台名称", examples=["bilibili"]),
    user_id: str = Path(..., description="用户ID", examples=["520500365"])
):
    """
    检测指定平台的账号是否存在
    
    - **platform**: 平台名称（如 bilibili）
    - **user_id**: 用户ID
    
    返回统一的 RESTful 格式响应
    """
    try:
        # 获取对应平台的服务
        service = ServiceFactory.get_service(platform)
        
        # 验证用户ID格式
        if not await service.validate_user_id(user_id):
            raise InvalidParameterException(
                parameter="user_id",
                message=f"无效的 {platform} 用户ID格式"
            )
        
        # 检查账号是否存在
        exists = await service.check_account_exists(user_id)
        
        if exists:
            return success_response(
                data={
                    "platform": platform,
                    "user_id": user_id,
                    "exists": True
                },
                message="账号存在"
            )
        else:
            return success_response(
                data={
                    "platform": platform,
                    "user_id": user_id,
                    "exists": False
                },
                message="账号不存在"
            )
            
    except InvalidParameterException as e:
        return error_response(code=400, message=e.message)
    except PlatformNotSupportedException as e:
        return error_response(code=400, message=e.message)
    except APIRequestException as e:
        return error_response(code=502, message=e.message, error_detail=e.error_detail)
    except Exception as e:
        return error_response(code=500, message="服务器内部错误", error_detail=str(e))


@router.get("/{platform}/{user_id}/info", summary="获取指定平台账号的详细信息")
async def get_account_info(
    platform: str = Path(..., description="平台名称", examples=["bilibili"]),
    user_id: str = Path(..., description="用户ID", examples=["520500365"])
):
    """
    获取指定平台账号的详细信息
    
    - **platform**: 平台名称
    - **user_id**: 用户ID
    
    返回用户的完整信息
    """
    try:
        # 获取对应平台的服务
        service = ServiceFactory.get_service(platform)
        
        # 验证用户ID格式
        if not await service.validate_user_id(user_id):
            raise InvalidParameterException(
                parameter="user_id",
                message=f"无效的 {platform} 用户ID格式"
            )
        
        # 获取用户信息
        user_info = await service.get_user_info(user_id)
        
        return success_response(
            data={
                "platform": platform,
                "user_id": user_id,
                "info": user_info
            },
            message="获取成功"
        )
        
    except AccountNotFoundException as e:
        return error_response(code=404, message=e.message)
    except InvalidParameterException as e:
        return error_response(code=400, message=e.message)
    except PlatformNotSupportedException as e:
        return error_response(code=400, message=e.message)
    except APIRequestException as e:
        return error_response(code=502, message=e.message, error_detail=e.error_detail)
    except Exception as e:
        return error_response(code=500, message="服务器内部错误", error_detail=str(e))


@router.get("/platforms", summary="获取支持的平台列表")
async def get_supported_platforms():
    """获取所有支持的平台列表"""
    return success_response(
        data={
            "platforms": ServiceFactory.get_supported_platforms(),
            "count": len(ServiceFactory.get_supported_platforms())
        },
        message="获取成功"
    )
