import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import CriticalTokkenError, ResponseError

RETRY_PERIOD = 600


ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'


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

""" Примите пж))) уже не могу)))."""

logger = logging.getLogger(__name__)
load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


def check_tokens():
    """Проверка переменных окружения."""
    try:
        for name in TOKEN_NAMES:
            if not globals()[name]:
                raise CriticalTokkenError(f"Неверно определенно: {name}")
    except KeyError as error:
        raise CriticalTokkenError(error)


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        logger.info('Начало отправки')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Отправленно сообщение "{message}"')
    except telegram.error.TelegramError:
        logger.exception(f'Ошибка при отправке сообщения "{message}"')
    else:
        logger.debug(f'Сообщение {message} успешно отправлено.')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    PAYLOADS = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params=PAYLOADS)
        logger.info('Запрос отправлен.')
    except requests.exceptions.RequestException as error:
        raise ResponseError(f'Ошибка {error}')
    if response.status_code != HTTPStatus.OK:
        raise ConnectionError('Не удалось получить ответ от API,'
                              f'ошибка: {response.status_code}')
    return response.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    logging.debug('Начало проверки')
    if not isinstance(response, dict):
        raise TypeError(
            f'Ответ не соответствует документации, {type(response)}'
        )
    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError('Ответ содержит не верные ключи')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(
            f'Ответ не соответствует документации, {type(homeworks)}'
        )


def parse_status(homework):
    """Извлечение статуса из информации о конкретной домашней работе."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    verdict = HOMEWORK_VERDICTS.get(status)
    if 'homework_name' not in homework:
        raise KeyError('Ошибка в получении имени домашней работы.')
    if 'status' not in homework:
        raise KeyError('Ошибка в получении статуса работы.')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Данный статус в HOMEWORK_VERDICTS не найден.')
    logger.info('Изменился статус проверки работы')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logger.debug('Бот работает.')
    try:
        check_tokens()
    except Exception as error:
        logger.critical(f'Критическая ошибка:{error}.')
        sys.exit('Отсутсвуют переменные окружения.')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    prev_message = None
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homeworks = response.get('homeworks')
            if homeworks:
                message = parse_status(homeworks[0])
                if message != prev_message:
                    send_message(bot, message)
                    prev_message = message
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s, %(levelname)s, %(message)s'
                        )
    main()
