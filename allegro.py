import json
from pprint import pprint

import requests

CLIENT_ID = "b2d7f898ee684c9b9c08468fe45a20a4"  # wprowadź Client_ID aplikacji
CLIENT_SECRET = ""  # wprowadź Client_Secret aplikacji
TOKEN_URL = "https://allegro.pl/auth/oauth/token"
LISTING_URL = "https://api.allegro.pl/offers/listing"


def get_access_token():
    try:
        data = {'grant_type': 'client_credentials'}
        access_token_response = requests.post(TOKEN_URL, data=data, verify=False, allow_redirects=False,
                                              auth=(CLIENT_ID, CLIENT_SECRET))
        tokens = json.loads(access_token_response.text)
        access_token = tokens['access_token']
        return access_token
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def search_card(token, card):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.allegro.public.v1+json',
    }
    params = {
        "phrase": card,
        "fallback": "false",
        "seller.login": "Roki_94",
        "searchMode": "REGULAR"
    }
    response = requests.get(LISTING_URL, params=params, headers=headers)
    pprint(response)


def main():
    access_token = get_access_token()
    print("access token = " + access_token)

    search_card(access_token, "Tax")


if __name__ == "__main__":
    main()
