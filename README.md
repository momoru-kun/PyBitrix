# PyBitrix

![version](https://img.shields.io/pypi/v/pybitrix?color=%237c4dff&style=for-the-badge)

![downloads](https://img.shields.io/pypi/dd/pybitrix?style=for-the-badge)

---
PyBitrix is my lightweight implementation of Bitrix 24 REST API wrapper that I use in my own applications/integrations

## Requirements

- Python 3.6+
- requests
- aiohttp

---

## Quick start

### Install package from pip

```sh
pip3 install pybitrix
```

### Then create PyBitrix instance

```python
from pybitrix import PyBitrix

# for webhook usage
webhook = "https://You/hook from/bitrix/developers panel/"
b24 = PyBitrix(inbound_hook=webhook)

# for use as application (with tokens)
domain = "BX DOMAIN (eg. some-stuff.bitrix.ru). Can be taken from bitrix request to your app"
auth_id = "ACCESS_TOKEN_TAKEN_FROM_BITRIX_REQUEST_TO_YOUR_APP"
refresh_id = "REFRESH_TOKEN_TAKEN_FROM_BITRIX_REQUEST_TO_YOUR_APP"
app_id = "APP_ID_FROM_MARKETPLACE_OR_LOCAL_APP_INSTALLATION"
app_secret = "SECRET_KEY_FROM_MARKETPLACE_OR_LOCAL_APP_INSTALLATION"
b24 = PyBitrix(domain=domain, access_token=auth_id, refresh_token=refresh_id, app_id=app_id, app_secret=app_secret)
```

### Make call

```python
bx24.call('crm.contact.list', {
    'order': ['DSC'],
    'select': ['TITLE', 'DATE_CREATE'],
    'filter': {"<ID": 50}
})
```

### Make batch call

```python
batch={
    'contacts': 'crm.contact.list', 
    'deals': 'crm.deal.list'
}
batchParams={
    'contacts': [
        'select[]=TITLE', 
        'order[ID]=DSC', 
        'filter[>ID]=15'
    ], 'deals' : [
        'select[]=TITLE',
        'select[]=STAGE_ID'
    ]
}
response = bx24.callBatch(batch=batch, batchParams=batchParams)
print("CONTACTS: {}".format(response['result']['result']['contacts']))
print("DEALS: {}".format(response['result']['result']['deals']))
```

### Renew tokens

PyBitrix refreshes tokens automatically, but if you want to do this manually, you should call method `refresh_tockens()`

```python
bx24.refresh_tokens()
```

### asyncio + aiohttp

To use async version, you need to just import `PyBitrixAsync`

```python
    from pybitrix import PyBitrixAsync
    b24 = PyBitrixAsync(...)
    result = await b24(...)
```

---

## Todos

- More comfortable batchParams collector
- Fast lists uploading via `'start': -1`

## License

MIT
