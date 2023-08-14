from logging import getLogger, StreamHandler
from clients.database_client import SQLiteClient
from clients.telegram_client import TelegramClient
from workers.reminder import Reminder
import datetime
import time
from dotenv import load_dotenv
import os

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel('INFO')

load_dotenv()
TOKEN = os.getenv('TOKEN')
FROM_TIME = os.getenv('FROM_TIME')
TO_TIME = os.getenv('TO_TIME')
REMINDER_PERIOD = float(os.getenv('REMINDER_PERIOD'))
SLEEP_CHECK_PERIOD = float(os.getenv('SLEEP_CHECK_PERIOD'))

database_client = SQLiteClient(os.path.dirname(os.getcwd()) + '/users.db')
telegram_client = TelegramClient(token=TOKEN,
                                 base_url='https://api.telegram.org')
reminder = Reminder(database_client=database_client, telegram_client=telegram_client)
reminder.setup()

start_time = datetime.datetime.strptime(FROM_TIME, '%H:%M').time()
end_time = datetime.datetime.strptime(TO_TIME, '%H:%M').time()
while True:
    now_time = datetime.datetime.now().time()
    if start_time <= now_time <= end_time:
        reminder()
        time.sleep(REMINDER_PERIOD)
    else:
        time.sleep(SLEEP_CHECK_PERIOD)