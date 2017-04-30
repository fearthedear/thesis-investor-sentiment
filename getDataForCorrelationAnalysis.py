import dataset 
import config

db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.hostfrank+'/'+config.database)

#target: week, year, bull_bear, symbol

result = db.query (
	"""
	select week(time, 3) as month, year(time) as year, avg(sentimentBool) as percentage_bullish, symbol

	from messages_w_sentiment_v2

	where date(time) between 20140101 and 20161231
	and symbol = 'SPY'

	group by month,year
	order by year,month
	"""
	)

dataset.freeze(result, format='csv', filename='SPY_mweekly.csv')

