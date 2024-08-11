import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from datetime import datetime
import time

start_time = time.time()
pages = []
for page_number in range(1, 155):
    url_start = 'https://www.centralcharts.com/en/price-list-ranking/'
    url_end = 'ALL/asc/ts_19-us-nasdaq-stocks--qc_1-alphabetical-order?p='
    url = url_start + url_end + str(page_number)
    pages.append(url)

webpage = requests.get(pages[0])
soup = bs(webpage.text, 'html.parser')
stock_table = soup.find('table', class_='tabMini tabQuotes')
th_tag_list = stock_table.find_all('th')

headers = []
for each_tag in th_tag_list:
    title = each_tag.text
    headers.append(title)

headers[0] = 'Name'

new_headers = []
for header in headers:
    if header not in ('Cap.', 'Issued Cap.', ''):
        new_headers.append(header)
headers = new_headers
stock_df = pd.DataFrame(columns = headers)

 
for page in pages:
    webpage = requests.get(page)
    soup = bs(webpage.text, 'html.parser')

    
    if soup.find('table'):
        stock_table = soup.find('table', class_='tabMini tabQuotes')
        tr_tag_list = stock_table.find_all('tr')

        
        for each_tr_tag in tr_tag_list[1:]:
            td_tag_list = each_tr_tag.find_all('td')

            row_values = []
            for each_td_tag in td_tag_list[0:7]:
                new_value = each_td_tag.text.strip()
                row_values.append(new_value)

            stock_df.loc[len(stock_df)] = row_values


stock_df[['Name', 'Current price', 'Change(%)', 'Open','High', 'Low']] = \
    stock_df[['Name', 'Current price', 'Change(%)', 'Open', 'High', 'Low']] \
    .astype(str)

stock_df.replace({'Current price': {',':'', '-':'1'},
                  'Change(%)': {',':'', '-':'1', '%':''},
                  'Open': {',':'', '-':'1'},
                  'High': {',':'', '-':'1'},
                  'Low': {',':'', '-':'1'},
                  'Volume': {',':'', '-':'1'}
}, regex=True, inplace=True)

stock_df[['Current price', 'Change(%)', 'Open', 'High', 'Low', 'Volume']] = \
    stock_df[['Current price', 'Change(%)', 'Open', 'High', 'Low', 'Volume']]. \
    apply(pd.to_numeric)

stock_df = stock_df.sort_values(by=['Volume'], ascending=False)
print(stock_df)
stock_df.to_csv('stock_data.csv', index=False)

top_10_stock_df = stock_df.sort_values(by='Volume', ascending=False).head(10)
names = top_10_stock_df['Name']
volumes = top_10_stock_df['Volume']
fig = plt.figure()
ax = plt.subplot()
bar_plot = ax.barh(names, volumes, color='green')
container = ax.containers[0]
ax.bar_label(container, labels=[f'{x:,.0f}' for x in container.datavalues], fontsize=6, padding=3)
current_volumes = plt.gca().get_xticks()
plt.gca().set_xticklabels([f'{x:,.0f}' for x in current_volumes], rotation=45)
ax.set_xlabel('Trading Volume')
ax.set_ylabel('Company Name')

now = datetime.now()
todays_date = now.strftime('%m/%d/%y')
ax.set_title('Top 10 NASDAQ Stocks by Volume for ' + todays_date)

plt.tight_layout()
ax.set_xmargin(0.2)
ax.xaxis.set_minor_locator(MultipleLocator(2500000))
ax.grid(which='major', axis='x', color='lightgrey', linestyle='-', linewidth='1')
start_time = time.time()
print("--- %s seconds ---" % (time.time() - start_time))
plt.show()

