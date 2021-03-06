import sys; sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import dataset 
import config
import datetime
import yahooDownloader
from scipy import stats
import datetime
import calendar

# suppress mysqldb warnings
from warnings import filterwarnings
import MySQLdb as Database
filterwarnings('ignore', category = Database.Warning)



#connect local
#dblocal = dataset.connect('mysql://root:root@localhost/thesis_test')


def runRegression(symbol, value, aggregated, lag):
	#connect aws rds frankfurt
	db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.hostfrank+'/'+config.database)	

	######################
	####### VALUES #######
	######################
	stock = symbol
	change = True if value == 'Change' else False
	monthWeek = 'week' if aggregated == 'Weekly' else 'month'

	timeStart = ['2014','01','01']
	timeEnd = ['2016', '12','31']

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
			"select week(time,7) as week, year(time) as year, avg(sentimentBool) as percentage_bullish "
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

	#pass date, get price, if not trading day, go back a day
	def getPrice(day):
			try:
				return hdDf.loc[hdDf.index == str(day.date()), 'Open'].item()
			except:
				day2 = day + datetime.timedelta(days=1)
				return getPrice(day2)

	## add return column, calc returns with lag and insert
	## add return column, calc returns with lag and insert
	def addReturnWeeklyAgg():
		return_list = []
		day0_list = []
		day1_list = []
		for i in range(0, len(rdf)):
			#calc return
			day0 = datetime.datetime.strptime(str(rdf.iloc[i]['year'])+'-'+'W'+str(rdf.iloc[i][monthWeek]) + '-1', "%Y-W%W-%w")
			if lag > 0:
				day0 = day0 + datetime.timedelta(days=int(lag)*7)
			day1 = day0 + datetime.timedelta(days=7)
			
			day0_list.append(day0.day)
			day1_list.append(day1.day)
			price0 = getPrice(day0)
			price1 = getPrice(day1)

			stockReturn = (price1-price0)/price0
			return_list.append(stockReturn)

		return_series = pd.Series(return_list)
		day0_series = pd.Series(day0_list)
		day1_series = pd.Series(day1_list)
		rdf['Return'] = return_series.values
		rdf['Day0'] = day0_series.values
		rdf['Day1'] = day1_series.values


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


	print(x)
	print(y)
	slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

	results = { "p-value": p_value, "r-squared": r_value**2, "slope": slope}
	return results


