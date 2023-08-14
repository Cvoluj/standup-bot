import telebot
from telebot.types import Message
from datetime import datetime
from dotenv import load_dotenv
import os
from clients.telegram_client import TelegramClient
from clients.database_client import SQLiteClient
from actioners import UserActioner
from logging import getLogger, StreamHandler
from datetime import date

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel('INFO')

load_dotenv()
TOKEN = os.getenv('TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')


class MyBot(telebot.TeleBot):
    def __init__(self, telegram_client: TelegramClient, user_actioner: UserActioner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_client = telegram_client
        self.user_actioner = user_actioner

    def setup_resources(self):
        self.user_actioner.setup()

    def shutdown_resources(self):
        self.user_actioner.shutdown()

    def shutdown(self):
        self.shutdown_resources()


telegram_client = TelegramClient(token=TOKEN, base_url="https://api.telegram.org")
user_actioner = UserActioner(SQLiteClient('users.db'))
bot = MyBot(token=TOKEN, telegram_client=telegram_client, user_actioner=user_actioner)
bot.setup_resources()


@bot.message_handler(commands=['start'])
def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    isRegistred = False

    user = bot.user_actioner.get_user(user_id=str(user_id))
    if not user:
        bot.user_actioner.create_user(user_id=str(user_id), username=username, chat_id=chat_id)
        isRegistred = True
    bot.reply_to(message=message,
                 text=f"Ви {'вже' if not isRegistred else 'були'} зареєстровані,{' як:' if isRegistred else ''} {username}.\n"
                      f'Ваш id: {user_id}')


# callback function, if it get signal this function will wait until some actions will happen
def handle_standup_speech(message: Message):
    bot.user_actioner.update_date(user_id=str(message.from_user.id), updated_date=date.today())
    bot.send_message(chat_id=ADMIN_CHAT_ID, text=f'Користувач {message.from_user.username} сказав: {message.text}')
    bot.reply_to(message, text='Дякую за відповідь!')


@bot.message_handler(commands=['say_standup_speech'])
def say_standup_speech(message: Message):
    bot.reply_to(message, text="Привіт! Чим ти займався вчора? Що будеш робити сьогодні, які виникають труднощі?")

    bot.register_next_step_handler(message, handle_standup_speech)


def create_err_message(err: Exception) -> str:
    return f'Error catched at: {datetime.now()}\n{err.__class__} ::: {err}'


while True:
    try:
        bot.setup_resources()
        bot.polling()
    except Exception as err:
        error_message = create_err_message(err)
        bot.telegram_client.post(method='sendMessage', params={'text': create_err_message(err),
                                                               'chat_id': ADMIN_CHAT_ID})
        logger.error(error_message)
        bot.shutdown()
