import re
from bs4 import BeautifulSoup
import os
import time
import requests
from random import randint

i2 = 'MIME search png _ SGCommand _ Fandom.html'
i = open(i2, 'r', encoding='utf8')
soup = BeautifulSoup(i, "html.parser")
urls = soup.find_all('a', href=re.compile(r'nocookie'))
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
    }

for item in urls:
    final_string = re.sub(r'\/revision\/latest\?cb=.+', r'', item['href'])
    final_string2 = os.path.basename(final_string)
    endpoint = os.path.join('images', final_string2)
    if not os.path.exists(endpoint):
        r = requests.get(item['href'], headers=headers)
        with open(endpoint, 'wb') as cover_jpg:
            cover_jpg.write(r.content)
            print(item['href'], item['title'])
            rand_int = randint(1, 4)
            time.sleep(rand_int)
