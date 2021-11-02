# Caleb Flaherty, HW 6, 2/23/20

import pandas as pd
import matplotlib.pyplot as plt

IPOpath = 'C:/Users/caleb/Documents/School/FIN 4550 Python for Finance/Python Finance - Slides, etc/Homework 6/ipoData.csv'
IPOinfo = 'C:/Users/caleb/Documents/School/FIN 4550 Python for Finance/Python Finance - Slides, etc/Homework 6/ipoCRSP.csv'

IPOdata    = pd.read_csv(IPOpath,low_memory = False)
dateFilter = ((IPOdata.BEGPRC > 20100000) & (IPOdata.BEGPRC < 20190000))
exchFilter = ((IPOdata.HPRIMEXC == 'Q') | (IPOdata.HPRIMEXC == 'N'))
filtered   = IPOdata[dateFilter & exchFilter]
#pd.DataFrame(filtered.HTICK.unique()).to_csv('C:/Users/caleb/Documents/School/FIN 4550 Python for Finance/Python Finance - Slides, etc/Homework 6/tickers.csv') # to get tickers for crsp

crsp = pd.read_csv(IPOinfo,index_col = None)
crsp['DIVAMT'] = crsp.DIVAMT.fillna(0)
# crsp.loc[0,'RET'] = 0
firstObs = (crsp.groupby('TICKER').cumcount() == 0)
crsp.loc[firstObs,'initialShr'] = 500/crsp.PRC
crsp['initialShr'] = crsp.initialShr.fillna(0)
crsp['initialShr'] = crsp.groupby('TICKER').initialShr.cumsum()
crsp['value'] = crsp.initialShr * crsp.PRC

pfolio = crsp.groupby('date').value.sum().reset_index(0)
pfolio['RET']   = (pfolio.value - pfolio.value.shift(1))/pfolio.value.shift(1)
pfolio.loc[0,'RET'] = 0
pfolio['RET_plus1'] = pfolio.RET + 1

SPYbench = crsp[(crsp['TICKER'] == 'SPY')]

QQQbench = crsp[((crsp['TICKER'] == 'QQQQ') | (crsp['TICKER'] == 'QQQ'))]

x = pfolio.date
y = pfolio.RET
legend = []
fig, ax = plt.subplots()  	
ax.plot(x, y, color='k', lw=1.5)
ax.set_xlabel('Date')
ax.set_ylabel('% Return',color='k')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# plt.show() # 2. Shows plot of the portfolio. Ugly because no split date info. 

scatPfolio = pd.DataFrame()
scatPfolio['means'] = pd.to_numeric(crsp.groupby('TICKER').RET.mean())
scatPfolio['risk']  = pd.to_numeric(crsp.groupby('TICKER').RET.std())
print(scatPfolio)
# ax = scatPfolio.plot.scatter(x = 'risk', y = 'means')
# ax.set_ylim(-.05, .1)
# plt.rcParams.update({'font.size' : 30})
# plt.axhline(y = 0, color = 'black')
# plt.show()

scatQQQ = pd.DataFrame()
scatQQQ['means'] = QQQbench.RET.mean()   # Error I'm getting says there's "No numeric types to aggregate." So tried the pd.to_numeric function and it didn't work either.
scatQQQ['risk']  = QQQbench.RET.std()    # So I'm not sure what to do to get the scatter plots to work.

scatSPY = pd.DataFrame()
scatSPY['means'] = SPYbench.RET.mean()
scatSPY['risk']  = SPYbench.RET.std()

def getHPR(returns,months):
    recentReturns = returns[-months:].prod()
    geoMeanMonth  = recentReturns**(1/months)-1
    geoMeanYear   = (geoMeanMonth + 1)**(12)
    return(round(geoMeanYear-1,4))

HPR1year  = getHPR(pfolio.RET_plus1,12)
HPR3year  = getHPR(pfolio.RET_plus1,36)
HPR5year  = getHPR(pfolio.RET_plus1,60)
HPR10year = getHPR(pfolio.RET_plus1,120)

SPYbench1  = getHPR(SPYbench.RET_plus1,12)
SPYbench3  = getHPR(SPYbench.RET_plus1,36)
SPYbench5  = getHPR(SPYbench.RET_plus1,60)
SPYbench10 = getHPR(SPYbench.RET_plus1,120)

QQQbench1  = getHPR(QQQbench.RET_plus1,12)
QQQbench3  = getHPR(QQQbench.RET_plus1,36)
QQQbench5  = getHPR(QQQbench.RET_plus1,60)
QQQbench10 = getHPR(QQQbench.RET_plus1,120)

print(" ---  Abnormal Returns of Portfolio  --- ")
print("1 year Portfolio",HPR1year, "; 1-year SPY:",SPYbench1, "; 1-Year QQQ:",QQQbench1,"; Abnormal Return SPY",round(HPR1year-SPYbench1,4))
print("3 year Portfolio",HPR3year, "; 3-year SPY:",SPYbench3, "; 3-Year QQQ:",QQQbench3,"; Abnormal Return SPY",round(HPR3year-SPYbench3,4))
print("5 year Portfolio",HPR5year, "; 5-year SPY:",SPYbench5, "; 5-Year QQQ:",QQQbench5,"; Abnormal Return SPY",round(HPR5year-SPYbench5,4))
