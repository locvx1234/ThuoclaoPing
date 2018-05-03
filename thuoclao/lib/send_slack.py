from urllib import request, parse
import json

# get link :  https://my.slack.com/services/new/incoming-webhook/
webhook_url = "https://hooks.slack.com/services/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"

text = """
*Hello slacker!!!*

```
Status : OK 
Number : 23
```
"""

class Slack(object):
    def send_slack_message(self, text):
        payload = {"text": "{0}".format(text)}
    
        try:
            json_data = json.dumps(payload)
            req = request.Request(webhook_url,
                                data=json_data.encode('ascii'),
                                headers={'Content-Type': 'application/json'}) 
            resp = request.urlopen(req)
        except Exception as em:
            print("EXCEPTION: " + str(em))
 
slack = Slack() 
slack.send_slack_message(text)