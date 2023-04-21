import logging
import os
import sys
import time
from http import HTTPStatus

import exceptions
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

LAST_PROJECT = [0]


logger = logging.getLogger(__name__)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logging.info('Начало отправки')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError as error:
        logging.error(f'Сообщение отправлено {error}')
    else:
        logging.debug(f'Сообщение отправлено {message}')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    logging.debug('Отправляем запрос к эндпоинту API-сервиса')
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT, headers=headers, params=params)
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
    """Проверяет ответ API на соответствие документации."""
    logging.debug('Начало проверки')
    if not isinstance(response, dict):
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


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Отсутствует переменные')
        sys.exit('Отсутсвуют переменные окружения')
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
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s, %(levelname)s, %(message)s'
                        )
    main()
