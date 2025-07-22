from environs import Env

env = Env()
env.read_env()

CHANNEL_ID = 'onebillionne'  # Пример: @MyChannel
BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN")  # Замените на токен вашего бота
REGISTRATION_URL = 'https://1wqvwb.life/casino/list?open=register&p=r6w8'  # Ссылка на сайт регистрации
MINI_APP_URL = 'https://yourwebsite.com/miniapp'  # Ссылка на мини-приложение
INSTRUCTION_TEXT = 'Это текст инструкции. Замените на ваш текст.'  # Замените на вашу инструкцию
ADMIN_USERNAME = '@bezbak'  # ID чата админа
WELCOME_IMAGE = "images/main.png"
