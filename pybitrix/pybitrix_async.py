from pybitrix import PyBitrix

import aiohttp
import asyncio
import json

class PyBitrixAsync(PyBitrix):

    async def refresh_tokens(self) -> dict:
        """Refresh access token from Bitrix OAuth server
        :return: dict with refreshing status  
        """

        # Make call to oauth server
        result = None
        async with aiohttp.ClientSession() as session:
            async with session.post(self.oauth_url, json= {
                'grant_type': 'refresh_token',
                'client_id': self.access_token,
                'client_secret': self.app_secret,
                'refresh_token': self.refresh_token
            }) as response:
                result = await response.text

        try:
            result_json = json.loads(result)

            # Renew tokens
            self.auth_token = result_json['access_token']
            self.refresh_token = result_json['refresh_token']
        except (ValueError, KeyError):
            return {'status': False, 'error': 'Error on decode OAuth response', 'response': result}

        return {'status': True}

    async def call(self, method: str, params: dict = {}) -> dict:
        """ Makes call to bitrix24 REST and return result
        :param method: REST API Method you want to call
        :params: Request params
        :return: Call result
        """

        result = {}
        if self.inbound_hook:
            uri = self.inbound_hook + '/' + method
        else:
            uri = self.endpoint + method
            params['auth'] = self.access_token

        result = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(uri, json=params) as response:
                    r = await response.text
                    result = json.loads(r)

        except aiohttp.exceptions.ReadTimeout:
            return {'status': False, 'error': 'Timeout waiting expired'}
        except aiohttp.exceptions.ConnectionError:
            if 'https://' in self.endpoint:
                self.endpoint = self.endpoint.replace('https://', 'http://')
                return await self.call(method, params)
            else:
                return {'status': False, 'error': 'Could not connect to bx24 resource', 'uri': uri}

        while result.get('error') == 'QUERY_LIMIT_EXCEEDED':
            await asyncio.sleep(0.5)
            async with aiohttp.ClientSession() as session:
                async with session.post(uri, json=params) as response:
                    r = await response.text
                    result = json.loads(r)

        if result.get('error') == 'NO_AUTH_FOUND' or result.get('error') == 'expired_token':
            result = self.refresh_tokens()
            if result['status'] is not True:
                return result

            # Repeat API request after renew token
            result = await self.call(method, params)

        return result

    async def callBatch(self, batch: dict, batch_params: dict = {}, halt=False) -> dict:
        """ Creates Bitrix Batch and calls them
        :param batch: Dict  with call name and method to call in batch. Eg. {"deals": "crm.deal.list", "fields": "crm.deal.fields"}
        :param halt: Stop batch if error in method 
        :batch params: Params for batch methods. Eg. {"deals": ['select[]=TITLE', 'order[ID]=DSC', 'filter[<ID]=92']}
        :return: Batch result
        """
        request = {'halt': halt}

        for key, params in batch_params.items():
            for param in range(0, len(params)):
                if param == 0:
                    batch[key] += "?{}".format(batch_params[key][param])
                else:
                    batch[key] += "&{}".format(batch_params[key][param])

        request['cmd'] = batch
            
        result = await self.call('batch', request)
        return result