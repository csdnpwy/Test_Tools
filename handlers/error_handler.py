
class CustomError(Exception):
    """
    自定义异常类
    """
    def __init__(self, message):
        super().__init__(message)
