import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import re
import time
from discord import Webhook, RequestsWebhookAdapter
import tabulate


webhook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter())

url = requests.get(
    'https://www.collectorscache.com/catalog/pokemon_sealed_products-pokemon_booster_boxes/386?filter_by_stock=in-stock')
now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

soup = bs(url.content, 'html.parser')

products = soup.find_all('div', class_='meta')

data_list = []
for product in products:
    instock = re.findall('[0-9]+', product.find('span', class_='variant-short-info variant-qty').text.strip())
    data = dict(product_name=product.find('h4', class_='name small-12 medium-4').text.strip(),
                price=product.find('span', class_='regular price').text.strip(), in_stock_qty=instock[0])
    data_list.append(data)

time.sleep(5)
page_num = range(2, 11, 1)
for i in page_num:
    url = requests.get(
        'https://www.collectorscache.com/catalog/pokemon_sealed_products-pokemon_booster_boxes/386?filter_by_stock=in-stock&page=' + str(
            i) + '&sort_by_price=0')
    soup = bs(url.content, 'html.parser')

    products = soup.find_all('div', class_='meta')

    for product in products:
        instock = re.findall('[0-9]+', product.find('span', class_='variant-short-info variant-qty').text.strip())
        data = dict(product_name=product.find('h4', class_='name small-12 medium-4').text.strip(),
                    price=product.find('span', class_='regular price').text.strip(), in_stock_qty=instock[0])
        data_list.append(data)

    time.sleep(5)

df = pd.DataFrame(data_list)
df['price'] = df['price'].str.replace(r'$', '', regex=True).str.replace(r',', '', regex=True).str.strip()
df['price'] = df['price'].apply(pd.to_numeric)
df['product_name'] = df['product_name'].str.replace(r'Pokemon', '', regex=True).str.replace(r'MINT', '', regex=True)
df.sort_values(by=['price'], ascending=True, inplace=True)

df.to_csv('collectors_cache.csv', index=False)
discord_send = df.head(10)
print(tabulate.tabulate(discord_send, headers='keys', tablefmt='psql', showindex=False))
webhook.send(tabulate.tabulate(discord_send, headers='keys', tablefmt='psql', showindex=False))
