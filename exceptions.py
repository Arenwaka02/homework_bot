class NotForSending(Exception):
    """Не для пересылки в телеграм."""
    pass


class MyTelegramError(Exception):
    pass 