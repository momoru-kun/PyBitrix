from time import time, sleep

import requests
import json

class PyBitrix:
    """Class for working with Bitrix24 REST API"""
    def __init__(self, inbound_hook:str=None, domain="", access_token ="", refresh_token="", app_id="", app_secret=""):
        """Bitrix24 Constructor
        :param inbound_hook: If you access Bitrix REST API via inbound webhook"  
        :param domain: Bitrix24 domain (returns in GET params with key 'DOMAIN' when requesting your app)
        :param auth_token: Auth token
        :param refresh_token: Refresh token for reveal new access token - if you think than you don't need to refresh tokens leave it blank
        :param app_id: Your local (or marketplace) application ID - if you think than you don't need to refresh tokens leave it blank 
        :param app_secret: Your local (or marketplace) application secret key - if you think than you don't need to refresh tokens leave it blank
        """

        self.last_request_time = 0
        if inbound_hook != None:
            self.inbound_hook = inbound_hook
        else:
            self.inbound_hook = False
            self.oauth_url = 'https://oauth.bitrix.info/oauth/token/'
            self.endpoint = "https://{domain}/rest/".format(domain=domain)
            self.access_token = access_token
            self.refresh_token = refresh_token
            self.app_id = app_id
            self.app_secret = app_secret


    def refresh_tokens(self) -> dict:
        """Refresh access token from Bitrix OAuth server
        :return: dict with refreshing status  
        """
        
        # Make call to oauth server
        result = requests.post(self.oauth_url, json={
            'grant_type': 'refresh_token', 
            'client_id': self.client_id, 
            'client_secret': self.client_secret, 
            'refresh_token': self.refresh_token
        }).text

        try:
            result_json = json.loads(result)

            # Renew tokens
            self.auth_token = result_json['access_token']
            self.refresh_token = result_json['refresh_token']
        except (ValueError, KeyError):
            return {'status': False, 'error': 'Error on decode OAuth response', 'response': result}

        return {'status': True}

    def call(self, method:str, params:dict=None) -> dict:
        """ Makes call to bitrix24 REST and return result
        :param method: REST API Method you want to call
        :params: Request params
        :return: Call result
        """
        if self.last_request_time - time() <= 0.5:
            # Bitrix requests rate limitation is 2 req per second. 
            # So if we have requests delta less than 0.5, we need to suspend our request for a 0.9 second (in theory, is synced world we can't reach rate like this but anyway :) 
            sleep(0.9) 

        result = {}
        if self.inbound_hook:
            uri = self.inbound_hook + '/' + method
        else:
            uri = self.endpoint + method
            params['auth'] = self.access_token
        
        r = ""
        try:
            r = requests.post(uri, json=params).text
            result = json.loads(r)
        except requests.exceptions.ReadTimeout:
            return {'status': False, 'error': 'Timeout waiting expired'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'error': 'Could not connect to bx24 resource', 'uri': uri}
        except ValueError:
            self.last_request_time = time()
            return {'status': False, 'error': 'Error on decode BX24 response', 'response': r}
        
        if result.get('error') in ('NO_AUTH_FOUND', 'expired_token'):
            result = self.refresh_tokens()
            if result['stauts'] is not True:
                return result
            
            # Repeat API request after renew token
            result = self.call(method, params)

        self.last_request_time = time()
        return result

    def callBatch(self, batch: dict, batch_params:dict = {}, halt=False) -> dict:
        """ Creates Bitrix Batch and calls them
        :param batch: Dict  with call name and method to call in batch. Eg. {"deals": "crm.deal.list", "fields": "crm.deal.fields"}
        :param halt: Stop batch if error in method 
        :batch params: Params for batch methods. Eg. {"deals": ['select[]=TITLE', 'order[ID]=DSC', 'filter[<ID]=92']}
        :return: Batch result
        """
        if self.inbound_hook:
            uri = self.inbound_hook + '/' + 'batch'
        else:
            uri = self.endpoint + 'batch'
            batch['auth'] = self.access_token

        for key, params in batch_params.items():
            for param in range(0, len(params)):
                if param == 0:
                    batch[key] += "?{}".format(batch_params[key][param])
                else:
                    batch[key] += "&{}".format(batch_params[key][param])

        r=""
        result={}
        try:
            r = requests.post(uri, json=({'halt': halt, 'cmd': batch}))
            result = json.loads(r.text)
        except requests.exceptions.ReadTimeout:
            return {'status': False, 'error': 'Timeout waiting expired'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'error': 'Could not connect to bx24 resource', 'uri': uri}
        except ValueError:
            return {'status': False, 'error': 'Error on decode BX24 response', 'response': r}
        
        if result.get('error') in ('NO_AUTH_FOUND', 'expired_token'):
            result = self.refresh_tokens()
            if result['stauts'] is not True:
                return result
            
            # Repeat API request after renew token
            result = self.callBatch(batch)
        return result