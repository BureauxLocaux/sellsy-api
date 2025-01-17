import json
import logging
import time

import requests_oauthlib
import oauthlib.oauth1 as oauth1
from .errors import SellsyAuthenticateError, SellsyError, SellsyTooManyRequestsError

DEFAULT_URL = 'https://apifeed.sellsy.com/0/'


logger = logging.getLogger('sellsy_api')


class Client:
    def __init__(self, consumer_token, consumer_secret, user_token, user_secret, url=DEFAULT_URL):
        self.url = url
        self.session = requests_oauthlib.OAuth1Session(
            consumer_token,
            consumer_secret,
            user_token,
            user_secret,
            signature_method=oauth1.SIGNATURE_PLAINTEXT,
            signature_type=oauth1.SIGNATURE_TYPE_BODY
        )

    def api(self, method='Infos.getInfos', params={}, retry=True):
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

        # Handle sellsy too many requests (429 status code returned)
        if response.status_code == 429:
            if retry:
                logger.info("Too many calls made to the Sellsy API. Will perform a new attempt...")
                time.sleep(1)
                return self.api(method, params, retry=False)
            raise SellsyTooManyRequestsError()

        # Error handler
        response_json = response.json()
        if response_json['status'] == 'error':
            # To ease debugging of sellsy errors, we log the full response from Sellsy since it
            # may contain extra information we need.
            logger.error("An error occurred while calling the Sellsy API: " + json.dumps(response_json))
            error_code, error_message = response_json['error']['code'], response_json['error']['message']
            raise SellsyError(error_code, error_message)

        return response_json['response']


if __name__ == '__main__':
    import os

    consumer_token = os.environ.get('SELLSY_CONSUMER_TOKEN')
    consumer_secret = os.environ.get('SELLSY_CONSUMER_SECRET')
    user_token = os.environ.get('SELLSY_USER_TOKEN')
    user_secret = os.environ.get('SELLSY_USER_SECRET')

    client = Client(
        consumer_token,
        consumer_secret,
        user_token,
        user_secret)

    try:
        prospect = client.api(method='Prospects.getOne', params={
            'id': 10340097
        })
    except SellsyAuthenticateError as e:
        print('Authentication failed ! Details : {}'.format(e))
    except SellsyError as e:
        print(e)
