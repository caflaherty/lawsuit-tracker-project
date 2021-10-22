# Class Action Lawsuit Tracker Project

# importing packages
from typing import Match
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.keys import Keys
import re
import itertools
geckoPath = r'C:\Users\caleb\Documents\School\Grad\MSIS 5193\Libraries\geckodriver.exe'
driver = webdriver.Firefox(executable_path=geckoPath)

# navigate to yahoo finance biggest day losers section
yahooUrl = 'https://finance.yahoo.com/losers'
driver.get(yahooUrl)

# grabbing top 25 tickers from the 'losers' page
dayLosersTi = driver.find_elements_by_xpath('//a[@class="Fw(600) C($linkColor)"]') # xml path for the ticker
dayLosersNm = driver.find_elements_by_xpath('//td[@class="Va(m) Ta(start) Px(10px) Fz(s)"]') # xml path for the company name
dayLosersPr = driver.find_elements_by_xpath('//td/fin-streamer[@data-field="regularMarketPrice"]') # xml path for price. Will need to convert this to a float later to filter >5
dayLosersCh = driver.find_elements_by_xpath('//td/fin-streamer[@data-field="regularMarketChange"]') # convert to float later
dayLosersPc = driver.find_elements_by_xpath('//td/fin-streamer[@data-field="regularMarketChangePercent"]') # percent change
dayLosersMC = driver.find_elements_by_xpath('//td/fin-streamer[@data-field="marketCap"]') # market cap

Day_Losers_Ti=[]
Day_Losers_Nm=[]
Day_Loser_Pr =[]
Day_Losers_Ch =[]
Day_Losers_Pc =[]
Day_Losers_MC =[]

for (a, b, c, x, y, z) in itertools.zip_longest(dayLosersTi, dayLosersNm, dayLosersPr, dayLosersCh, dayLosersPc, dayLosersMC):
    Day_Losers_Ti.append(a.text)
    Day_Losers_Nm.append(b.text)
    Day_Loser_Pr.append(c.text)
    Day_Losers_Ch.append(x.text)
    Day_Losers_Pc.append(y.text)
    Day_Losers_MC.append(z.text)

yahoo_data_frame=pd.DataFrame({'DayLosersTi': Day_Losers_Ti, 'Day Losers Name': Day_Losers_Nm, 'Price':Day_Loser_Pr, 'Change':Day_Losers_Ch, '%Change': Day_Losers_Pc, 'MC': Day_Losers_MC})

print(yahoo_data_frame)

# Eliminate penny stocks (those with value under $5 [or at least those under $1])

url_template ='https://finance.yahoo.com/quote/Ticker?p=Ticker'

#Get the URL that has the list of articles for each ticker
 
articles_by_ti_url=[]

for element in Day_Losers_Ti:
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

ti_article_df= pd.DataFrame({'Ticker': ti_label_list, 'Article Title':headlineList})

#Filter to get just articles with keywords

ti_article_df_filtered = ti_article_df[ti_article_df['Article Title'].str.contains("(Investors|Shareholders|Attorneys|Investigation|LLP|Law Firm)")]

print(ti_article_df_filtered)

# headlines
# exUrl = 'https://finance.yahoo.com/quote/NVAX?p=NVAX'
# driver.get(exUrl)

# headlines = driver.find_elements_by_xpath('//h3[@class="Mb(5px)"]/a[@class]')

# headlineList = []
# for x in headlines:
#     headlineList.append(x.text)

# headlineList

# regex for headlines with 'law firm', 'shareholders', 'attorneys', 'investigation', 'LLP'
# lawsuits = re.findall('(Investors)', str(headlineList))
# lawsuits

# we can run this daily or something and save a CSV just to have the tickers and their respective losses on hand to track performance.

driver.quit()