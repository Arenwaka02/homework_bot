import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import CriticalTokkenError

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


logger = logging.getLogger(__name__)
load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}


def check_tokens():
    """Проверка переменных окружения."""
    try:
        for name in TOKEN_NAMES:
            if not globals()[name]:
                raise CriticalTokkenError(f"Неверно определенно: {name}")
    except NameError as error:
        raise CriticalTokkenError(error)


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        logging.info('Начало отправки')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Отправленно сообщение "{message}"')
    except telegram.error.TelegramError:
        logger.exception(f'Ошибка при отправке сообщения "{message}"')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    PAYLOADS = {"from_date": timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        response = requests.get(
            ENDPOINT, headers=headers, params=PAYLOADS)
        logging.info('Запрос отправлен.')
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError('Нету соеденения с сервером.')
        if not isinstance(response.json(), dict):
            raise TypeError('Не словарь')
        else:
            logging.info('Ответ от api ---- 200')
            return response.json()
    except Exception as error:
        raise Exception(f'Ошибка {error}')


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    equivalent = ("homeworks", "current_date")
    if not isinstance(response, dict):
        raise TypeError(
            f"Ответ не соответствует документации, {type(response)}"
        )
    if not equivalent == tuple(response.keys()):
        raise KeyError("Ответ содержит не верные ключи")
    homeworks = response.get("homeworks")
    if not isinstance(homeworks, list):
        raise TypeError(
            f"Ответ не соответствует документации, {type(homeworks)}"
        )


def parse_status(homework):
    """Извлечение статуса из информации о конкретной домашней работе."""
    homework_name = homework.get("homework_name")
    status = homework.get("status")
    verdict = HOMEWORK_VERDICTS.get(status)
    if 'homework_name' not in homework:
        raise KeyError('Ошибка в получении имени')
    if 'status' not in homework:
        raise KeyError('Ошибка в получении имени')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Такого статуса в я нету')
    logging.info('Изменился статус проверки работы')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logging.debug("Бот работает")
    try:
        check_tokens()
    except Exception as error:
        logger.critical(f"Критическая ошибка:{error}")
        sys.exit("Отсутсвуют переменные окружения")

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    prev_report = ''
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
            logging.error(message)
            if message != prev_report:
                send_message(bot, message)
                prev_report = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s, %(levelname)s, %(message)s'
                        )
    main()
