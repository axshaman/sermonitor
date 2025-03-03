import requests
import json, xmltodict

user_api : str = 'http://xmlproxy.ru/search/'


def get_urls(user_api=user_api, query=''):
    # result = []
    # for page in range(6):
    url = f'{user_api}&query={query}'
    search_result = requests.get(url)
    xpars = xmltodict.parse(search_result.text)
    res = json.dumps(xpars,
                        sort_keys=False,
                        indent=4,
                        ensure_ascii=False,
                        separators=(',', ': '))
        # result = json.dumps(result.append(res)) 
    return res
