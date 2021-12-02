# scrape headlines

import pandas as pd
from pandas.core.arrays import boolean
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from time import sleep
from random import randint
geckoPath = r'C:\Users\caleb\Documents\School\Grad\MSIS 5193\Libraries\geckodriver.exe'
driver = webdriver.Firefox(executable_path=geckoPath)

csv = pd.read_csv('C:/Users/caleb/Documents/School/Grad/MSIS 5193/Project/CSVs/losers 11-29-2021.csv')

dayLoserTi = csv['DayLosersTi'].tolist()

url_template = 'https://finance.yahoo.com/quote/Ticker?p=Ticker'

articles_by_ti_url=[]

for element in dayLoserTi:
    insert_ti = url_template.replace("Ticker", element)
    articles_by_ti_url.append(insert_ti)
print(articles_by_ti_url)

#Headlines from each Ticker's URL

headlineList=[]
ti_label_list =[]
for link in articles_by_ti_url:
    driver.get(link)
    headlines = driver.find_elements_by_xpath('//*[@id="quoteNewsStream-0-Stream"]/ul/li/div/div/div[2]/h3/a')

    for element in headlines:
        headlineList.append(element.text)
        ti_label_list.append(link.split('?p=')[1:2])#create ticker label so we know which articles belong to which Ticker Url
    sleep(randint(5,12)) # added this to hopefully prevent IP blacklist

ti_article_df= pd.DataFrame({'Ticker': ti_label_list, 'Article Title':headlineList})

#Filter to get just articles with keywords

ti_article_df_filtered = ti_article_df[ti_article_df['Article Title'].str.contains("(Investors|Shareholders|Attorneys|Investigation|LLP|Law Firm|ALERT)")]

ti_article_df_filtered = ti_article_df_filtered.reset_index(drop=True)

print(ti_article_df_filtered)

ti_article_df_filtered.to_csv('11-29-2021 Loser Headlines.csv', index=False)

driver.quit()