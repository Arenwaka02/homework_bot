import logging
import os
import sys
import time
from http import HTTPStatus

import exceptions
import requests
import telegram
from dotenv import load_dotenv

from exceptions import (MessegeError, ResponseError,
                        UnknownStatusHomework)

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

<<<<<<< HEAD

TOKEN_NAMES = (
    "PRACTICUM_TOKEN",
    "TELEGRAM_TOKEN",
    "TELEGRAM_CHAT_ID",
)


def check_tokens():
    """Проверка переменных окружения."""
=======
LAST_PROJECT = [0]


logger = logging.getLogger(__name__)


def check_tokens():
    """Проверяет доступность переменных окружения."""
>>>>>>> 5a884f41e649351416ed540755182ff7fcc5bd5d
    return all([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot: telegram.Bot, message: str):
    """Отправка сообщения в Telegram чат."""
    try:
        logging.info('Начало отправки')
        bot.send_message(TELEGRAM_CHAT_ID, message)
<<<<<<< HEAD
        logger.debug(f'Отправленно сообщение "{message}"')
    except telegram.error.TelegramError:
        logger.exception(f'Ошибка при отправке сообщения "{message}"')
        raise MessegeError(f'Ошибка при отправке сообщения "{message}"')
=======
    except telegram.TelegramError as error:
        logging.error(f'Сообщение отправлено {error}')
    else:
        logging.debug(f'Сообщение отправлено {message}')
>>>>>>> 5a884f41e649351416ed540755182ff7fcc5bd5d


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
<<<<<<< HEAD
    PAYLOADS = {"from_date": timestamp}
=======
    logging.debug('Отправляем запрос к эндпоинту API-сервиса')
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': timestamp}
>>>>>>> 5a884f41e649351416ed540755182ff7fcc5bd5d
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


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    equivalent = ("homeworks", "current_date")
    if not isinstance(response, dict):
<<<<<<< HEAD
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
=======
        raise TypeError('Ошибка в ответе Api')
    if 'homeworks' not in response or 'current_date' not in response:
        raise TypeError('Пустой ответ')
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        raise TypeError('Не являтся списком')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус."""
    try:
        status = homework['status']
        verdict = HOMEWORK_VERDICTS[status]
        logging.debug(f'Статус работы: {status}')
    except KeyError as error:
        logging.error(f'Неверный статус домашних заданий {error}')
        raise f'Данные "статус" не найден, {error}'
    try:
        homework_name = homework['homework_name']
        logging.debug(f'Имя работы {homework_name}')
    except Exception as error:
        logging.error(f'не корректное имя {error}')
        raise f'Имя не корректно {error}'
    if homework.get('homework_name') is None:
        logging.error('Ключ "homework_name" не найден')
        raise KeyError('Ключ "homework_name" не найден')
    try:
        message = f'Изменился статус проверки работы "{homework_name}". ' \
                  f'{verdict}'
        if type(message) == str:
            logging.debug(type(message))
            return message
    except Exception as error:
        logging.error(f'return not string {error}, {type(message)}')
        raise f'return not string {error}, {status}, {type(message)}'
>>>>>>> 5a884f41e649351416ed540755182ff7fcc5bd5d


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
    if not check_tokens():
        logging.critical('Отсутствует переменные')
        sys.exit('Отсутсвуют переменные окружения')
<<<<<<< HEAD

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
=======
    logging.debug('Бот работает')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    anti_spam_check = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)[0]
            sending_message = parse_status(homeworks[LAST_PROJECT])
            if sending_message != anti_spam_check:
                logging.debug(f'Новый статус {sending_message}')

                if send_message(bot, sending_message):
                    logging.debug(f'Статус {sending_message}')
                    anti_spam_check = sending_message
            else:
                logging.debug('No changes')
            timestamp = response.get('current_date', timestamp)
        except Exception as error:
            message = f'Ошибка в работе {error}'
            logging.error(message)
            if message != anti_spam_check:
                if send_message(bot, message):
                    anti_spam_check = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
>>>>>>> 5a884f41e649351416ed540755182ff7fcc5bd5d
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s, %(levelname)s, %(message)s'
                        )
    main()
