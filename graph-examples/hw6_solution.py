import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from numpy import log

investDollars = 500
rcParams['font.sans-serif'] = ["Garamond"]

# Read CRSP data and clean
crsp = pd.read_csv("C:/Users/caleb/Documents/School/FIN 4550 Python for Finance/Python Finance - Slides, etc/Homework 6/ipoCRSP.csv")
crsp['PRC']    = abs(crsp.PRC)
crsp['DIVAMT'] = crsp.DIVAMT.fillna(0)
crsp['date']   = pd.to_datetime(crsp.date.astype(str),format='%Y%m%d')

# Find first observation of each TICKER (Date when shares are purchased) 
filtETFs = (crsp.TICKER !='QQQQ') | (crsp.TICKER !='QQQ') | (crsp.TICKER != 'SPY')
IPO      = crsp[filtETFs]
firstObs = IPO.groupby('TICKER').cumcount() == 0     					  # finds first instance of new tickers. Serves same purpose as line 16.
firstDates = IPO[firstObs].groupby('date').PRC.count().reset_index()      # subset with only first instance in dataset and groups by date and counts them.
firstDates = firstDates.rename(columns={'PRC':'IPO_count'})				  # formatting

# Create IPO Portfolio
IPO.loc[firstObs,'new_ipo'] = (investDollars / IPO.PRC)
IPO['new_ipo'] = IPO.new_ipo.fillna(0)
IPO['new_ipo'] = IPO.groupby('TICKER').new_ipo.cumsum()
IPO['divCash'] = IPO.new_ipo * IPO.DIVAMT
IPO['divCash'] = IPO.groupby('TICKER').divCash.cumsum()
IPO['value'] = IPO.new_ipo * IPO.PRC 
IPO = IPO.groupby('date').value.sum().reset_index().copy()
IPO.name = 'IPO'
# ^^ I'm using .copy() simply so that I don't need to worry about .LOC later ^^

# Create S&P 500 portfolio
SPY = crsp[crsp.TICKER == 'SPY']
SPY = SPY.merge(firstDates,on='date',how='left').fillna(0)
SPY['new_spy']    = (SPY.IPO_count * investDollars)/SPY.PRC
SPY['spy_shares'] = SPY.new_spy.cumsum()
SPY['divCash']    = (SPY.spy_shares * SPY.DIVAMT).cumsum()
SPY['value']   = SPY.spy_shares * SPY.PRC + SPY.divCash
SPY = SPY[['date','value']].copy()
SPY.name = 'SPY'

# Create NASDAQ-Index Portfolio
QQQ = crsp[(crsp.TICKER == 'QQQ') | (crsp.TICKER == 'QQQQ')]
QQQ = QQQ.merge(firstDates,on='date',how='left').fillna(0)
QQQ['new_qqq']    = (QQQ.IPO_count * investDollars)/QQQ.PRC
QQQ['qqq_shares'] = QQQ.new_qqq.cumsum()
QQQ['divCash']    = (QQQ.qqq_shares * QQQ.DIVAMT).cumsum()
QQQ['value']   = QQQ.qqq_shares * QQQ.PRC + QQQ.divCash
QQQ = QQQ[['date','value']].copy()
QQQ.name = 'QQQ'


# Calculate returns for chart
def monthlyReturnRisk(df,months):
	ret    = log(df.value/df.value.shift(1))
	monthAvg = ret.mean()
	monthStd = ret.std()
	return(monthAvg,monthStd,df.name)

scatData = pd.DataFrame(columns = ['means', 'risk','name'])
dfList = [IPO,SPY,QQQ]
for df in dfList:
	means,risk,name = monthlyReturnRisk(df,120)
	scatData.loc[df.name] = [means,risk,name]


# Line chart
x  = IPO.date
y1 = IPO.value
y2 = SPY.value
y3 = QQQ.value

fig, ax = plt.subplots()  	
ax.set_title("Portfolio Returns of IPOs \n VS. SPY and QQQ",fontsize=14)
ax.plot(x, y1, color='blue', lw=1.5,label="IPO Portfolio")
ax.plot(x, y2, color='red', lw=1.5,label="SPY Portfolio")
ax.plot(x, y3, color='orange', lw=1.5,label="QQQ Portfolio")
ax.set_xlabel("Date")
ax.set_ylabel("Growth of investing 500 per IPO date (000s)",fontsize=12)
ax.legend()
plt.show()



# Scatterplot
ax = scatData.plot.scatter(x='risk',y='means')
plt.axhline(y=0, color='black')
ax.set_ylim(-.05,.1)
# plt.show()

