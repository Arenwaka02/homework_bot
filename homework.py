import logging
import os
import sys
import time
from http import HTTPStatus

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
    if 'homework_name' not in homework:
        raise KeyError('Ошибка в получении имени')
    if 'status' not in homework:
        raise KeyError('Ошибка в получении имени')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError('Такого статуса в я нету')
    verdict = HOMEWORK_VERDICTS[homework_status]
    logging.info('Изменился статус проверки работы')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.CRITICAL('Отсутствует переменные')
        sys.exit('Отсутсвуют переменные окружения')
    logging.debug('Бот работает')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    current_report = []
    prev_report = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)[0]
            if not homeworks or homeworks == current_report:
                logging.debug('Новый статус проверки не появился')
            else:
                message = parse_status(homeworks[0])
                if message:
                    send_message(bot, message)
                    current_report = homeworks
        except Exception as error:
            message = f'Ошибка в работе {error}'
            logging.error(message)
            if message != prev_report:
                send_message(bot, message)
                prev_report = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s, %(levelname)s, %(message)s'
                        )
    main()
