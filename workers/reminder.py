from logging import getLogger, StreamHandler
from dotenv import load_dotenv
import os
from clients.telegram_client import TelegramClient
from clients.database_client import SQLiteClient


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel('INFO')
load_dotenv()
TOKEN = os.getenv('TOKEN')


class Reminder:
    GET_TASKS = """
    SELECT chat_id FROM users WHERE last_updated_date IS NULL OR last_updated_date < date('now');
    """

    def __init__(self, telegram_client: TelegramClient, database_client: SQLiteClient):
        self.telegram_client = telegram_client
        self.database_client = database_client
        self.isSetted = False

    def setup(self):
        self.database_client.create_conn()
        self.isSetted = True

    def shutdown(self):
        self.database_client.close_conn()

    def notify(self, chat_ids: list):
        for chat_id in chat_ids:
            res = self.telegram_client.post(method='sendMessage', params={'text': 'Тобі варто відписати як твої справи '
                                                                                  'тицьни:\n'
                                                                                  '/say_standup_speech',
                                                                          'chat_id': chat_id})
            logger.info(res)
        

    def execute(self):
        chat_ids = self.database_client.execute_select_command(self.GET_TASKS)
        if chat_ids:
            self.notify(chat_ids=[tuple_from_database[0] for tuple_from_database in chat_ids])

    def __call__(self, *args, **kwargs):
        if not self.isSetted:
            logger.error('Resources in worker has not been set up!')
            return
        self.execute()

if __name__ == '__main__':
    database_client = SQLiteClient(os.path.dirname(os.getcwd()) + '/users.db')
    telegram_client = TelegramClient(token=TOKEN,
                                     base_url='https://api.telegram.org')
    reminder = Reminder(database_client=database_client, telegram_client=telegram_client)
    reminder.setup()
    reminder()