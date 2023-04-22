class BaseException(Exception):
    """Базовое исключение."""
    pass


class ResponseError(BaseException):
    """Не верный ответ на запрос к API."""
    pass


class UnknownStatusHomework(BaseException):
    """Неверный статус домашней работы."""
    pass


class MessegeError(BaseException):
    """Ошибка отправки сообщения бота."""
    pass


class CriticalTokkenError(BaseException):
    """Ошибка отправки сообщения бота."""
    pass
