"""
自定义异常类
用于统一错误处理
"""


class AccountNotFoundException(Exception):
    """账号不存在异常"""
    def __init__(self, platform: str, user_id: str, message: str = "账号不存在"):
        self.platform = platform
        self.user_id = user_id
        self.message = message
        super().__init__(self.message)


class PlatformNotSupportedException(Exception):
    """平台不支持异常"""
    def __init__(self, platform: str, supported_platforms: list):
        self.platform = platform
        self.supported_platforms = supported_platforms
        self.message = f"不支持的平台: {platform}，支持的平台: {', '.join(supported_platforms)}"
        super().__init__(self.message)


class APIRequestException(Exception):
    """API 请求异常"""
    def __init__(self, platform: str, error_detail: str):
        self.platform = platform
        self.error_detail = error_detail
        self.message = f"{platform} API 请求失败: {error_detail}"
        super().__init__(self.message)


class InvalidParameterException(Exception):
    """无效参数异常"""
    def __init__(self, parameter: str, message: str = "参数无效"):
        self.parameter = parameter
        self.message = message
        super().__init__(self.message)
