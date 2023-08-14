# Standup bot
created according [luchanos](https://www.youtube.com/@luchanos) tutorial in Youtube
# Instalation

Clone project
```commandline
git clone https://github.com/Cvoluj/standup-bot.git
```

Create virtualenv
```commandline
python -m venv <name_of_virtualenv>
```
Install requirements
```commandline
pip intsall -r requirements.txt
```

Create .env file in work directory and set: 
```
TOKEN='<bot_token>'
ADMIN_CHAT_ID=<chat_admin_id>
FROM_TIME='<day_date_time_like_"18:00">'
TO_TIME='<day_date_time>'
REMINDER_PERIOD=<time_in_seconds>
SLEEP_CHECK_PERIOD=<time_in_seconds>
```

Run main.py and reminder_executor.py