import requests
from logs import logs
import json


class PushyAPI:

    @staticmethod
    def sendPushNotification(title, message, data, to, options):
        
        api_key = '295b5fff86dcfa091f47a7bff44c40665af2ec1c35f46f56bba89ca22bc98236'
        url = 'https://api.pushy.me/push?api_key=' + api_key
        post_data = options or {}

        post_data['to'] = to
        post_data['data'] = {'title': title, 'data': data, 'message': message}
        

        req = requests.post(url=url, json=post_data)
        if req.status_code == 200:
            logs.d("Уведомление отправлено", to, "успешно!")
        else:
            logs.error("Уведомление не отправлено", to, "!", "Status code:", req.status_code)