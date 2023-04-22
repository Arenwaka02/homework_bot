class BaseException(Exception):
    """Базовое исключение."""

    code_default: int = 0

    def __init__(self, message: str, code: int or str):
        self.message = message
        self.code = code or self.code_default


class ResponseError(BaseException):
    """Не верный ответ на запрос к API."""

    code_default: int = -2
    pass


class UnknownStatusHomework(BaseException):
    """Неверный статус домашней работы."""

    code_default: int = -3
    pass


class MessegeError(BaseException):
    """Ошибка отправки сообщения бота."""

    code_default: int = -4
    pass


class CriticalTokkenError(BaseException):
    """Ошибка отправки сообщения бота."""

    code_default: int = -1
    pass
