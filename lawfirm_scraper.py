# Script to scrape a few law firms websites for companies they are attempting to file class action suits against.

from os import name
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.keys import Keys
geckoPath = r'C:\Users\caleb\Documents\School\Grad\MSIS 5193\Libraries\geckodriver.exe'
driver = webdriver.Firefox(executable_path=geckoPath)

# this csv contains over 8000 rows of companies with their tickers and name. Will use it to match tickers to companies if one of these sites is missing either datum.
nasdaq = pd.read_csv("C:/Users/caleb/Documents/School/Grad/MSIS 5193/Project/CSVs/nasdaq_all_companies_ti_nm.csv")
nasdaq = nasdaq[nasdaq['Symbol'].map(len) <= 4] # this should remove warrants
nasdaq = nasdaq.reset_index(drop=True)
nasdaq['Name'] = nasdaq['Name'].str.replace('The ', '')
nasdaq['firstName'] = nasdaq['Name'].str.split(' ').str[0]
nasdaq.head()
len(nasdaq)

# KSF Counsel
ksfUrl = 'https://www.ksfcounsel.com/cases/'
driver.get(ksfUrl)

nameTicKsf = driver.find_elements_by_xpath('//h2[@class="entry-title"]')

nameTicListKsf = []
for x in nameTicKsf:
    nameTicListKsf.append(x.text)

nameTicListKsf
len(nameTicListKsf)

nameListKsf = [i.split(' (', 1)[0] for i in nameTicListKsf]
nameListKsf

ticListKsf = [i.split(': ', 1)[1] for i in nameTicListKsf]
ticListKsf = [i.split(')', 1)[0] for i in ticListKsf]
ticListKsf

ksfSuitDf = pd.DataFrame(
    {'DayLosersTi':ticListKsf,
    'Day Losers Name':nameListKsf}
)

ksfSuitDf['Firm'] = 'KSF Council'

ksfSuitDf
ksfSuitDf.to_csv('KSF Council Suits.csv')

# For the next three, I should be able to write a function to at least set up the initial dataframe before cleaning each one, but I just want it to work for now. 

# Thornton Law Firm
thorntonUrl = 'https://www.tenlaw.com/practice-areas/securities-litigation/'
driver.get(thorntonUrl)

namesThrn = driver.find_elements_by_xpath('//td/a')

namesthrnList = []
for x in namesThrn:
    namesthrnList.append(x.text)

namesthrnList
len(namesthrnList)

# turn the list of names into a dataframe so we can match the names with their tickers (list of tickers/names from NASDAQ, may need another source for other exchanges)
rawData = {'name1': namesthrnList} 
namesThrDf = pd.DataFrame(rawData , columns = ['name1'])
namesThrDf['name1'] = namesThrDf['name1'].str.replace('The ','')
namesThrDf['name1'] = namesThrDf['name1'].str.replace(',','')
# namesThrDf['name1'] = namesThrDf['name1'].str.rstrip('The ')
namesThrDf
namesThrDf['firstName'] = namesThrDf['name1'].str.split(' ').str[0]  # creating columns for merge
namesThrDf

nameTicThrDf = pd.merge(namesThrDf, nasdaq, on='firstName',how='left')
nameTicThrDf
nameTicThrDf = nameTicThrDf[nameTicThrDf['Symbol'].notna()]     # drop companies if not publicly traded
nameTicThrDf
nameTicThrDf = nameTicThrDf.drop([14,15,16])      # removed incorrect companies and warrants
nameTicThrDf = nameTicThrDf.drop(['firstName'], axis=1)
nameTicThrDf = nameTicThrDf.reset_index(drop=True)
nameTicThrDf['Firm'] = 'Thornton Law Firm'
nameTicThrDf = nameTicThrDf.drop([10]) # don't know why I have to do it this way but the correct SNAP doesn't show up after running line 77.
nameTicThrDf

nameTicThrDf.to_csv('Thornton Suits.csv')

# Schall Law
schallUrl = 'https://schallfirm.com/join-a-class-action/'
driver.get(schallUrl)

tableSchall = driver.find_elements_by_xpath('//tr') # entire table
schallName = driver.find_elements_by_xpath('//td[@class="title"]') # company name
# can add xpath selectors for the dates if we want them later to track performance from the date suit was announced. 

schallNameList = []
for x in schallName:
    schallNameList.append(x.text)

schallNameList

schallData = {'name1':schallNameList}
schallNameDf = pd.DataFrame(schallData, columns = ['name1'])
schallNameDf['name1'] = schallNameDf['name1'].str.replace('The ', '')
schallNameDf
# pretty much the same as above.
schallNameDf['firstName'] = schallNameDf['name1'].str.split(' ').str[0]
schallNameDf

nameTicSchDf = pd.merge(schallNameDf, nasdaq, on='firstName',how='left')
nameTicSchDf
nameTicSchDf = nameTicSchDf[nameTicSchDf['Symbol'].notna()]
len(nameTicSchDf)
nameTicSchDf['Firm'] = 'Schall Law Firm'
nameTicSchDf = nameTicSchDf.drop(['firstName'], axis=1)
nameTicSchDf = nameTicSchDf.drop([11,70,78])
nameTicSchDf = nameTicSchDf.drop(nameTicSchDf.index[37:55])
nameTicSchDf = nameTicSchDf.drop([37,38,39,40,41,42,43,44,45,46,47,48]) # probably a better way to do this but it works for now
nameTicSchDf = nameTicSchDf.drop([93,94,95,96,97,98,100,101,109,110,112])
nameTicSchDf = nameTicSchDf.reset_index(drop=True)
nameTicSchDf
len(nameTicSchDf)

nameTicSchDf.to_csv('Schall Suits.csv')

# Kaskela Law
kaskUrl = 'https://kaskelalaw.com/securities-class-action-litigation/'
driver.get(kaskUrl)

kaskName = driver.find_elements_by_xpath('//h3') # scrapes article title which is the company name

kaskNameList = []
for x in kaskName:
    kaskNameList.append(x.text)

kaskNameList

kaskData = {'name1':kaskNameList}
kaskNameDf = pd.DataFrame(kaskData, columns = ['name1'])
kaskNameDf['name1'] = kaskNameDf['name1'].str.replace(',', '')
kaskNameDf['firstName'] = kaskNameDf['name1'].str.split(' ').str[0]
len(kaskNameDf)
nameTicKasDf = pd.merge(kaskNameDf, nasdaq, on='firstName',how='left')
nameTicKasDf['Firm'] = 'Kaskela Law'
nameTicKasDf

nameTicKasDf.to_csv('Kaskela Law.csv')

driver.quit()