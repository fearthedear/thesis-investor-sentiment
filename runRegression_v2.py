import sys; sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import dataset 
import config
import datetime
import yahooDownloader
from scipy import stats
from bokeh.plotting import *
from bokeh.models import *
import datetime
import calendar

# suppress mysqldb warnings
from warnings import filterwarnings
import MySQLdb as Database
filterwarnings('ignore', category = Database.Warning)


#connect aws rds frankfurt
db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.hostfrank+'/'+config.database)
#connect local
#dblocal = dataset.connect('mysql://root:root@localhost/thesis_test')

######################
####### VALUES #######
######################

stock = raw_input("Enter stock symbol --> ")
#timeStart = map(str, raw_input("Enter timeframe start YYYY/MM/DD --> ").split('/'))
#timeEnd = map(str, raw_input("Enter timeframe end YYYY/MM/DD --> ").split('/'))
timeStart = ['2014','01','01']
timeEnd = ['2016', '12','31']

#select time sentiment is to be aggregated for 
sentAgg = raw_input("For what time period do you want to aggregate sentiment measure? Monthly or Weekly [M/W] --> ")
changeOr = raw_input('For the regression, use sentiment weekly change or absolute bullish percentage? ([C]hange/[A]bsolute) --> ')
monthWeek = 'week' if sentAgg.lower()=='w' else 'month' if sentAgg.lower() == 'm' else 'error'
change = True if changeOr.lower() == 'c' else False


if sentAgg == 'error':
	print('no valid input given')
	sys.exit()
#potentially add time for sentiment aggregate: day, week, month
lag = raw_input("Enter lag for regression in weeks/months --> ")

startDay, startMo, startY = timeStart[2], timeStart[1], timeStart[0]
endDay, endMo, endY = timeEnd[2], timeEnd[1], timeEnd[0]

#####################
### GET SENTIMENT ###
#####################

#get bullish percentage, grouped monthly, year
def getMonthlySentiment():
	return db.query(
		"select month(time) as month, year(time) as year, avg(sentimentBool) as percentage_bullish "
		"from messages_w_sentiment_v2 "
		"where date(time) between '"+startY+startMo+startDay +"' and '" +endY+endMo+endDay+"'"
		"and symbol = " + "'"+stock+"' "
		"group by month,year "
		"order by year,month "
	)

#get bullish percentage, grouped weekly,year
def getWeeklySentiment():
	return db.query( 
		"select week(time) as week, year(time) as year, avg(sentimentBool) as percentage_bullish "
		"from messages_w_sentiment_v2 "
		"where date(time) between '"+startY+startMo+startDay +"' and '" +endY+endMo+endDay+"'"
		"and symbol = " + "'"+stock+"' "
		"group by week,year "
		"order by year,week "
		)

#get bullish daily NOT WORKING, WIP
# result2 = db.query(
# 		"select date(time) as day, avg(sentimentBool) as percentage_bullish "
# 			"from messages_w_sentiment_v2 "
# 			"where date(time) between '"+startY+startMo+startDay +"' and '" +endY+endMo+endDay+"'"
# 			"and symbol = " + "'"+stock+"' "
# 			"group by day"
# 		)

#get sentiment depending on user input
result = getMonthlySentiment() if monthWeek == 'month' else getWeeklySentiment()

dataset.freeze(result, format='csv', filename=str(startY)+str(startMo)+str(startDay)+'-'+str(endY)+str(endMo)+str(endDay)+'_'+stock+'_bullish_percentage.csv')


########################
### GET STOCK PRICES ###
########################

#consider just downloading whole years here, filtering later
hdDf = yahooDownloader.download(stock,1,1,2014,31,3,2017)

##########################
### PREPARE REGRESSION ###
##########################

#create sentiment dataframe
sdf = pd.read_csv(str(startY)+str(startMo)+str(startDay)+'-'+str(endY)+str(endMo)+str(endDay)+'_'+stock+'_bullish_percentage.csv')

#add change to sentiment dataframe
if change:
	sentimentChange = [0]
	for i in range(1, len(sdf)):
		cha = (sdf.iloc[i]['percentage_bullish']-sdf.iloc[i-1]['percentage_bullish'])/sdf.iloc[i-1]['percentage_bullish']
		sentimentChange.append(cha)

	sentiment_change_series = pd.Series(sentimentChange)
	sdf['Sentiment_Change'] = sentiment_change_series.values


#create return dataframe with same length

## build dataframe with the timespan of the input, same lenght as sentimentdf
if monthWeek == 'month':
	rdf = sdf[['month', 'year']].copy()
else:
	rdf = sdf[['week', 'year']].copy()

#pass date, get price, if not trading day, go forward a day
def getPrice(day):
		try:
			return hdDf.loc[hdDf.index == str(day.date()), 'Open'].item()
		except:
			day2 = day + datetime.timedelta(days=1)
			return getPrice(day2)

## add return column, calc returns with lag and insert
def addReturnWeeklyAgg():
	return_list = []
	for i in range(0, len(rdf)):
		#calc return
		day0 = datetime.datetime.strptime(str(rdf.iloc[i]['year'])+'-'+'W'+str(rdf.iloc[i][monthWeek]) + '-1', "%Y-W%W-%w")
		if lag > 0:
			day0 = day0 + datetime.timedelta(days=int(lag)*7)
		day1 = day0 + datetime.timedelta(days=7)
		
		price0 = getPrice(day0)
		price1 = getPrice(day1)

		stockReturn = (price1-price0)/price0
		return_list.append(stockReturn)

	return_series = pd.Series(return_list)
	rdf['Return'] = return_series.values


def addReturnMonthlyAgg():

	return_list = []
	for i in range(0, len(rdf)):
		day0_year = int(rdf.iloc[i]['year'])
		day0_month = int(rdf.iloc[i]['month'])
		if lag > 0:
			day0_month += int(lag)
		if day0_month > 12:
			day0_year += 1
			day0_month -= 12

		day0 = datetime.datetime (day0_year, day0_month, 1)
		day1 = datetime.datetime (int(day0.year), int(day0.month), calendar.monthrange(int(day0.year), int(day0.month))[1] )

		price0 = getPrice(day0)
		price1 = getPrice(day1)

		stockReturn = (price1-price0)/price0
		return_list.append(stockReturn)

	return_series = pd.Series(return_list)
	rdf['Return'] = return_series.values



if monthWeek == 'week':
	addReturnWeeklyAgg()
else:
	addReturnMonthlyAgg()

##################
### REGRESSION ###
##################

if change:
	sdf.drop(sdf.head(1).index, inplace=True)
	rdf.drop(rdf.head(1).index, inplace=True)
	x = sdf['Sentiment_Change']
	y = rdf['Return']
else:
	x = sdf['percentage_bullish']
	y = rdf['Return']


slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
pvalue = "p-value: "+ str(p_value)
rsquared = "r-squared: "+ str(r_value**2)
slopep = "slope: " + str(slope)

############
### PLOT ###
############

# Generate regression line
r_x, r_y = zip(*((i, i*slope + intercept) for i in range(-15,15)))

p = figure (plot_width=400, plot_height=400)
output_file("regression.html")
p.line(r_x, r_y, color="red")
p.scatter(x, y, marker="square", color="blue")
p.title.text = stock
p.title.align = "center"
p.title.text_font_size = "25px"
p.xaxis.axis_label = 'Sentiment Change' if change else 'Bullish Percentage'
p.yaxis.axis_label = 'Return'
p.add_layout(Title(text=pvalue, align="center"), "below")
p.x_range = Range1d(x.min(), x.max()) if change else Range1d(0,1)
p.y_range = Range1d(-0.2, 0.2)
show(p)