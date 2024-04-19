import requests
url = "https://www.vanguardngr.com"
headers = {
    #"User-Agent": "PostmanRuntime/7.29.0",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    #"Postman-Token": "086e97b8-b15b-4c0b-89c8-ce2634d0b419",
    "Host": "www.vanguardngr.com",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

#headers =  {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}

r = requests.get(url, headers=headers)
print("headers", r.request.headers)
print(r.status_code)