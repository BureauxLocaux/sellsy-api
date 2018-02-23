import json
from requests_oauthlib import OAuth1, OAuth1Session
from errors import SellsyAuthenticateError, SellsyError

DEFAULT_URL = 'https://apifeed.sellsy.com/0/'

SIGNATURE_PLAINTEXT='PLAINTEXT'
SIGNATURE_TYPE_BODY='body'

class SellsyClient:
    def __init__(self, consumer_token, consumer_secret, user_token, user_secret, url=DEFAULT_URL):
        self.url = url
        self.session = OAuth1Session(
            consumer_token,
            consumer_secret,
            user_token,
            user_secret,
            signature_method=SIGNATURE_PLAINTEXT,
            signature_type=SIGNATURE_TYPE_BODY
        )

    def api(self, method='Infos.getInfos', params={}):
        headers = {'content-type': 'application/json', 'cache-control': 'no-cache'}
        payload = {'method': method, 'params': params}

        response = self.session.post(self.url, data={
            'request': 1, 
            'io_mode': 'json',
            'do_in': json.dumps(payload)
        }, headers=headers)

        # Handle OAuth error (401 status code returned)
        if response.status_code == 401:
            raise SellsyAuthenticateError(response.text)

        # Error handler
        response_json = response.json()
        if response_json['status'] == 'error':
            error_code, error_message = response_json['error']['code'], response_json['error']['message']
            raise SellsyError(error_code, error_message)

        return response_json['response']


if __name__=='__main__':
    import os

    consumer_token = os.environ.get('SELLSY_CONSUMER_TOKEN')
    consumer_secret = os.environ.get('SELLSY_CONSUMER_SECRET')
    user_token = os.environ.get('SELLSY_USER_TOKEN')
    user_secret = os.environ.get('SELLSY_USER_SECRET')

    client = SellsyClient(
        consumer_token,
        consumer_secret,
        user_token,
        user_secret)
        
    try:
        prospect = client.api(method='Prospects.getOnes', params={
            'id': 10340097
        })
    except SellsyAuthenticateError as e:
        print('Authentication failed ! Details : {}'.format(e))
    except SellsyError as e:
        print(e)