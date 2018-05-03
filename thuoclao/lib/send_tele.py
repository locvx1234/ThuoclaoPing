import requests

### CHANGE THESE ###
telegram_bot_token = '518593888:AAExHxExaTD9XzY9WAkRnIDexjbkGDhsnO4'
chat_id = '481523352'

text = """
*Hello world!!!*

```
Status : OK 
Number : 23
```
"""
####################

class Telegram(object):
    def __init__(self, token, chat_id):
        self.token = token 
        self.chat_id = chat_id

    def send_telegram_message(self, text):
        url = 'https://api.telegram.org/bot{0}/sendMessage'.format(self.token)
        data = {'chat_id':self.chat_id, 'text':text, 'parse_mode':'Markdown'}
        requests.post(url=url, data=data).json()

tele = Telegram(telegram_bot_token, chat_id)
tele.send_telegram_message(text)
