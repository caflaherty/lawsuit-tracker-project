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
import matplotlib.pyplot as plt
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.chunk import conlltags2tree, tree2conlltags
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

# start sentiment analysis of Yahoo comments. ###########################################################################################################
tickerCommentDf = pd.read_csv('C:/Users/caleb/Documents/School/Grad/MSIS 5193/Project/CSVs/Loser Comments.csv')
tickerCommentDf['Ticker'] = tickerCommentDf['Ticker'].str.replace("[\[\]\"']", "")
tickerCommentDf = tickerCommentDf.loc[:, ~tickerCommentDf.columns.str.contains('^Unnamed')]
tickerCommentDf.head()
tickerCommentDf.to_csv('Loser Comments.csv')

commentDf = pd.read_csv('C:/Users/caleb/Documents/School/Grad/MSIS 5193/Project/CSVs/Loser Comments.csv')

stop = stopwords.words('english')
commentDf['Comment'] = commentDf['Comment'].apply(lambda x: ' '.join(x for x in x.split() if x not in stop))

numPattern = '\\b[0-9]+\\b'

commentDf['Comment'] = commentDf['Comment'].str.replace(numPattern,'')

puncPattern = '[^\w\s]'

commentDf['Comment'] = commentDf['Comment'].str.replace(puncPattern,'')

commentDf['Comment'] = commentDf['Comment'].apply(lambda x: ' '.join(x.lower() for x in x.split()))

ridNamesWords = ['novavax','zillow','solarwind', 'playtika','rollins','marathon','lifestance','snapchat','zillow group','lemonade','ginkgo','bioworks','bright health','paysafe','oscar', 'tuya','intelligent systems',
                    'cassava','vipshop','firstcash','stoneco','shift','mirati','cronos','faraday','oatly','tg','oak street','theralink','lightspeed','chegg','vroom','cereval']

commentDf['Comment'] = commentDf['Comment'].apply(lambda x: ' '.join(x for x in x.split() if x not in ridNamesWords))

porstem = PorterStemmer()

commentDf['Comment'] = commentDf['Comment'].apply(lambda x: ' '.join([porstem.stem(word) for word in x.split()]))

vectorizer = CountVectorizer()
tokenData = pd.DataFrame(vectorizer.fit_transform(commentDf['Comment']).toarray(), columns=vectorizer.get_feature_names())

vectorizer = CountVectorizer(max_df=0.8, min_df=4, stop_words='english')
docTermMatrix = vectorizer.fit_transform(commentDf['Comment'].values.astype('U'))
docTermMatrix.shape

LDA = LatentDirichletAllocation(n_components=4, random_state=36)
LDA.fit(docTermMatrix)

firstTopic = LDA.components_[0]
topTopicWords = firstTopic.argsort()[-10:]

for i in topTopicWords:
    print(vectorizer.get_feature_names()[i])

for i, topic in enumerate(LDA.components_):
    print(f'Top 10 words for each topic #{i}: ')
    print([vectorizer.get_feature_names()[i] for i in topic.argsort()[-10:]])
    print('\n')

# add a new column to the dataframe
topicValues = LDA.transform(docTermMatrix)
topicValues.shape
commentDf['topic'] = topicValues.argmax(axis=1)
commentDf.head()

# Creating NMF groups.
tfidfVect = TfidfVectorizer(max_df=0.8, min_df=4, stop_words='english')
docTermMatrix2 = tfidfVect.fit_transform(commentDf['Comment'].values.astype('U'))

nmf = NMF(n_components=4, random_state=48)
nmf.fit(docTermMatrix2)

firstNmfTopic = nmf.components_[0]
topNmfWords = firstNmfTopic.argsort()[-10:]

for i in topNmfWords:
    print(tfidfVect.get_feature_names()[i])

for i, topic in enumerate(nmf.components_):
    print(f'Top 10 words for topic #{i}: ')
    print([tfidfVect.get_feature_names()[i] for i in topic.argsort()[-10:]])
    print('\n')

# add a new column to the dataframe
topicValues2 = nmf.transform(docTermMatrix2)
commentDf['topics2'] = topicValues2.argmax(axis=1)
commentDf.head()

commentDf.head()

commentDf.to_csv('groupedComments.csv')

############ Sentiment Analysis ############
features = tickerCommentDf['Comment']

vectorizer = TfidfVectorizer(max_features=250, min_df=7, max_df=0.8, stop_words=stop)

processed_features = vectorizer.fit_transform(features).toarray()

############ Named Entity Recognition ############
ogComments = pd.read_csv('C:/Users/caleb/Documents/School/Grad/MSIS 5193/Project/CSVs/Loser Comments.csv')

# df.groupby(['name', 'month'], as_index = False).agg({'text': ' '.join})
combinedComments = ogComments.groupby(['Ticker'], as_index = False).agg({'Comment':' '.join})
combinedComments.to_csv('longcomment.csv')

combinedComments['tokenComments'] = combinedComments.apply(lambda row: nltk.word_tokenize(row['Comment']), axis=1)

combinedComments

combinedComments['results'] = combinedComments.tokenComments.apply(lambda x: nltk.ne_chunk(pos_tag(word_tokenize(x))))

driver.quit()

