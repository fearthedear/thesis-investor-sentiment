import sys; sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import dataset 
import config
import yahooDownloader
from scipy import stats
from bokeh.plotting import *
from bokeh.models import *

#connect aws rds frankfurt
db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.hostfrank+'/'+config.database)
#connect local
dblocal = dataset.connect('mysql://root:root@localhost/thesis_test')

#####################
### INSERT VALUES ###
#####################

#for sentiment:
year='2016'
stock='ZTS'

stock = raw_input("Enter stock symbol --> ")
year = raw_input("Enter year --> ")

#for stockPrices:
startDay, startMo, startY = 01, 01, int(year)
endDay, endMo, endY = 31, 12, int(year)

#####################
### GET SENTIMENT ###
#####################

#get bullish percentage
result = db.query( 
		"select week(time) as week, avg(sentimentBool) as percentage_bullish "
		"from messages_w_sentiment_v2 "
		"where year(time) = " + year + " "
		"and symbol = " + "'"+stock+"' "
		"group by week"
		)

dataset.freeze(result, format='csv', filename=year+'_'+stock+'_bullish_percentage.csv')



########################
### GET STOCK PRICES ###
########################

#download from yahoo, insert into local db/AWS, maybe modification, save to csv
hdDf = yahooDownloader.download(stock,startDay,startMo,startY,endDay,endMo,endY)

temp = db['temp']
for i in range(0, len(hdDf.index)-1):
	temp.insert(dict(date=hdDf.iloc[i].name,price=hdDf.iloc[i]['Adj Close']))

#creating table with avg weekly stock price
db.query("create table temp2 select avg(price) as price, week(date) as week from temp group by week")

result2 = db.query("select week, price from temp2")
dataset.freeze(result2, format='csv', filename=year+'_'+stock+'_stock_prices.csv')

db.query('drop table temp') 
db.query('drop table temp2')

#create dataframes, one with weekly sentiment, one with return a month later synced to that
#creating dataframes
sdf = pd.read_csv(year+'_'+stock+'_bullish_percentage.csv')
pdf = pd.read_csv(year+'_'+stock+'_stock_prices.csv')

#create return+4 weeks df from price df
rdf_list = []

for i in range(0, len(pdf.index)-4):
	rdf_list.append((pdf.iloc[i+4]['price']-pdf.iloc[i]['price'])/pdf.iloc[i]['price'])

rdf = pd.DataFrame(rdf_list, columns=['return'])


##################
### REGRESSION ###
##################

#get length of return dataframe, set sentiment df to that length
sdf.drop(sdf.week[len(rdf.index):], inplace=True)


x = sdf['percentage_bullish']
y = rdf['return']

#regression = np.polyfit(x, y, 1)

slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
print("p-value: "+ str(p_value))
print("r-squared: "+ str(r_value**2))
print("slope: " + str(slope))


############
### PLOT ###
############


# Generate regression line
r_x, r_y = zip(*((i, i*slope + intercept) for i in range(15)))

p = figure (plot_width=400, plot_height=400)
output_file("regression.html")
p.line(r_x, r_y, color="red")
p.scatter(x, y, marker="square", color="blue")
#p.title = "Regression "+ stock + " in "+year
p.xaxis.axis_label = 'Bullish Percentage'
p.yaxis.axis_label = 'Return'
p.x_range = Range1d(0, 1)
p.y_range = Range1d(-1, 1)
show(p)
