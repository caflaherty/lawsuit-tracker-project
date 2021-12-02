# Scrape twitter for sentiment around tickers

# scrape imports
import glob
import os
from random import randint
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

# sentiment imports
import numpy
import nltk
from nltk.stem import PorterStemmer
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.chunk import conlltags2tree, tree2conlltags
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, plot_confusion_matrix 
# all of them just to be safe

# combine all CSVs into one
csvPath = 'C:/Users/caleb/Documents/School/Grad/MSIS 5193/Project/CSVs/Headlines'
headlineCsvs = glob.glob(csvPath + '/*.csv')
lawsuitDf = pd.concat((pd.read_csv(f) for f in headlineCsvs), ignore_index=True)
lawsuitDf = lawsuitDf.loc[:, ~lawsuitDf.columns.str.contains('^Unnamed')]
lawsuitDf['Ticker'] = lawsuitDf['Ticker'].astype(str)
lawsuitDf['Ticker'] = lawsuitDf['Ticker'].str.replace("[\[\]\"']", "")
lawsuitDf.head()

countCos = lawsuitDf['Ticker'].value_counts().reset_index().rename(
            columns={'index':'Ticker', 'Ticker':'Count'})
countCosDf = pd.DataFrame(countCos)
countCosDf.head()
countCosDf.to_csv('countLawsuits.csv')

lawsuitDf.to_csv('lawsuitCos.csv')

loserDf = pd.read_csv('C:/Users/caleb/Documents/School/Grad/MSIS 5193/countLawsuits.csv')

# remove duplicate tickers from dataframe
# resultDf = loserDf.drop_duplicates(subset=['DayLosersTi'], keep='first')
# resultDf = resultDf.reset_index(drop=True)
# resultDf = resultDf.loc[:, ~resultDf.columns.str.contains('^Unnamed')]
# resultDf = resultDf[resultDf['Price'] > 5]
# len(resultDf)

# resultDf.to_csv('finalLosersNoDupes.csv')

tickerList = loserDf['Ticker'].tolist()

urlTemplate = 'https://finance.yahoo.com/quote/ticker/community?p=ticker'

tickerCommentsUrl = []
for x in tickerList:
    tickerUrl = urlTemplate.replace('ticker', x)
    tickerCommentsUrl.append(tickerUrl)

commentList = []
commentTicker = []
for y in tickerCommentsUrl:
    driver.get(y)
    comments = driver.find_elements_by_xpath('//div[@class="C($c-fuji-grey-l) Mb(2px) Fz(14px) Lh(20px) Pend(8px)"]')
    for z in comments:
        commentBody = z.get_attribute('textContent')
        commentList.append(commentBody)
        commentTicker.append(y.split('?p=')[1:2])
    sleep(randint(5, 12))

tickerCommentDf = pd.DataFrame({'Ticker':commentTicker, 'Comment':commentList})

tickerCommentDf.head()

tickerCommentDf.to_csv('Loser Comments.csv')

# start sentiment analysis of Yahoo comments. ###########################################################################################################
tickerCommentDf = pd.read_csv('C:/Users/caleb/Documents/School/Grad/MSIS 5193/Loser Comments.csv')
tickerCommentDf['Ticker'] = tickerCommentDf['Ticker'].str.replace("[\[\]\"']", "")
tickerCommentDf.head()

multiComment = tickerCommentDf.set_index(['Ticker', 'Comment'])
multiComment.head()

multiComment.to_csv('comments by company.csv')


# Navigate to twitter and search for the tickers
twtrUrl = 'https://twitter.com/i/flow/login'
driver.get(twtrUrl)

twtrUser = driver.find_element_by_xpath('//input[@class]')
twtrUser.send_keys('caleb_flaherty' + Keys.ENTER)
twtrPW = driver.find_element_by_name('password')
twtrPW.send_keys('' + Keys.ENTER) # password is from a password generator, so it's unique. won't post on github.

twtrSrch = driver.find_element_by_xpath('//input[@class="r-30o5oe r-1niwhzg r-17gur6a r-1yadl64 r-deolkf r-homxoj r-poiln3 r-7cikom r-1ny4l3l r-xyw6el r-641cr4 r-1dz5y72 r-fdjqy7 r-13qz1uu"]')
twtrSrch.send_keys('$SNAP' + Keys.ENTER) # testing before defining a function. 

twtrBody = driver.find_elements_by_xpath('//div/div/div[@class="css-901oao r-1fmj7o5 r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0"]')

tweetList = []
for z in twtrBody:
    tweetList.append(z.text)

# make a function to search all tickers in the dataframe
def tweetScrape(ticker):
    twtrSrch = driver.find_element_by_xpath('//input[@class="r-30o5oe r-1niwhzg r-17gur6a r-1yadl64 r-deolkf r-homxoj r-poiln3 r-7cikom r-1ny4l3l r-xyw6el r-641cr4 r-1dz5y72 r-fdjqy7 r-13qz1uu"]')
    for x in loserDf['DayLosersTi']:
        ticker = x
        twtrSrch.send_keys(ticker + Keys.ENTER) # change 'ticker' to the tickers from our dataframe. fix for deliverable 2.


driver.quit()

# scrape x many tweets from around the day the stock fell the most. Use this for sentiment analysis. 
# scrape yahoo finance historical page for price movement from the day the stock ended up on the list. 