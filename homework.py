import logging
import os
import requests
import sys
import telegram
import time

from dotenv import load_dotenv
from exceptions import (
    CriticalTokkenError,
    MessegeError,
    ResponseError,
    UnknownStatusHomework,
)
from http import HTTPStatus
from logging.handlers import RotatingFileHandler


logger = logging.getLogger(__name__)
load_dotenv()

PRACTICUM_TOKEN = os.getenv("YP_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}


RETRY_PERIOD = 600


ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"


HOMEWORK_VERDICTS = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}


TOKEN_NAMES = (
    "PRACTICUM_TOKEN",
    "TELEGRAM_TOKEN",
    "TELEGRAM_CHAT_ID",
)

def check_tokens() -> None:
    """Проверка переменных окружения."""
    try:
        for name in TOKEN_NAMES:
            if not globals()[name]:
                raise CriticalTokkenError(f"Неверно определенно: {name}")
    except NameError as error:
        raise CriticalTokkenError(error)


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Отправленно сообщение "{message}"', exc_info=True)
    except telegram.error.TelegramError:
        logger.exception(f'Ошибка при отправке сообщения "{message}"')
        raise MessegeError(f'Ошибка при отправке сообщения "{message}"')


def get_api_answer(timestamp: int) -> dict:
    """Запрос к единственному эндпоинту API-сервиса."""
    PAYLOADS = {"from_date": timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=PAYLOADS,
        )
    except requests.exceptions as error:
        raise requests.ConnectionError(error)
    response_json = response.json()
    if response.status_code != HTTPStatus.OK:
        if set(response_json.keys()) == {'error', 'code'}:
            raise ResponseError(
                response_json.get('error').get('error'),
                response_json.get('code')
            )
        raise ResponseError(f'Неверный ответ запрооса {response.status_code}')
    return response_json


def check_response(response: dict) -> None:
    """Проверка ответа API на соответствие документации."""
    equivalent = ("homeworks", "current_date")
    if not isinstance(response, dict):
        raise TypeError(
            f"Ответ не соответствует документации, {type(response)} не dict"
        )
    if not equivalent == tuple(response.keys()):
        raise KeyError("Ответ содержит не верные ключи")
    homeworks = response.get("homeworks")
    if not isinstance(homeworks, list):
        raise TypeError(
            f"Ответ не соответствует документации, {type(homeworks)} не list"
        )


def parse_status(homework: dict) -> str:
    """Извлечение статуса из информации о конкретной домашней работе."""
    homework_name = homework.get("homework_name")
    status = homework.get("status")
    verdict = HOMEWORK_VERDICTS.get(status)
    if homework_name and status in list(HOMEWORK_VERDICTS.keys()):
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    raise UnknownStatusHomework(f'Неверный статус работы"{homework_name}"')


def main() -> None:
    """Основная логика работы бота."""
    try:
        check_tokens()
    except Exception as error:
        logger.critical(f"Критическая ошибка:{error}", exc_info=True)
        return -1

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homeworks = response.get("homeworks")
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
                timestamp = response.get("current_date")
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logging.exception(error)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    handler = RotatingFileHandler(
        "my_logger.log", maxBytes=500000, backupCount=5, encoding="utf-8"
    )
    logger.addHandler(handler)
    handler.setFormatter(formatter)
    main()
