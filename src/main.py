from cryptography.hazmat.primitives.asymmetric import ed25519
from urllib.parse import urlparse, urlencode
import urllib
import json
import requests
import os
import tzlocal

from dotenv import load_dotenv
from datetime import datetime

def url_concat(end) -> str:
    return "https://coinswitch.co" +  end
def env():
    load_dotenv()
    print("loaded api keys!")

def time() -> str:
    url = url_concat("/trade/api/v2/time")
    response = json.loads(requests.request("GET", url).text)
    timestamp = response['serverTime'] / 1000

    local_time = datetime.fromtimestamp(timestamp,tzlocal.get_localzone())
    return local_time.strftime("%Y-%m-%d %H:%M:%S.%f (%Z)")
def ping() -> bool:
    url = url_concat("/trade/api/v2/ping")

    response =  requests.request("GET", url)
    if response.status_code != 404:
        print("pinged " + url)
        return True
    else:
        print("could not ping " + url)
        return False
def validate(api_key, secret_key):
    if not ping():
        return None
    print("at", time())
    params = {}
    endpoint = "/trade/api/v2/validate/keys"
    url = url_concat(endpoint)
    method = "GET"
    payload = {}

    unquote_endpoint = endpoint
    if method == "GET" and len(params) != 0:
        endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
        unquote_endpoint = urllib.parse.unquote_plus(endpoint)

    signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)

    request_string = bytes(signature_msg, 'utf-8')
    secret_key_bytes = bytes.fromhex(secret_key)
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
    signature_bytes = secret_key.sign(request_string)
    signature = signature_bytes.hex()

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': signature,
        'X-AUTH-APIKEY': api_key
    }

    response = requests.request("GET", url, headers=headers, json=payload)
    if response.status_code == 200:  # Valid Access
        print("keys validated, signature generated!")
        return signature
    elif response.status_code == 401: # Invalid Access
        print("keys are invalid!")
        return None

def folio(api_key, sign):
    endpoint = "/trade/api/v2/user/portfolio"
    url = url_concat(endpoint)
    payload = {}

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': sign,
        'X-AUTH-APIKEY': api_key
    }

    response = requests.request("GET", url, headers=headers, json=payload)
    print(response.text)


def main():
    env()

    api_key = os.getenv("API_KEY")
    secret_key = os.getenv("SECRET_KEY")
    signature = validate(api_key, secret_key)
    folio(api_key, signature)



if __name__=="__main__":
    main()