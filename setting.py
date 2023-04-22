# Время повторного опроса
RETRY_PERIOD = 600

# Точка опроса
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"

# Наименование вывода ответов проверки
HOMEWORK_VERDICTS = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}

# Наименование необходимых переменных из .env
TOKEN_NAMES = (
    "PRACTICUM_TOKEN",
    "TELEGRAM_TOKEN",
    "TELEGRAM_CHAT_ID",
)
