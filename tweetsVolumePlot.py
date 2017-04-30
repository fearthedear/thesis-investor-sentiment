import sys; sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import dataset 
import config
import yahooDownloader
from scipy import stats
from bokeh.plotting import *
from bokeh.models import *

# suppress mysqldb warnings
from warnings import filterwarnings
import MySQLdb as Database
filterwarnings('ignore', category = Database.Warning)

def make_plot(stock):

	#get message volume
	#connect aws rds frankfurt
	db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.hostfrank+'/'+config.database)


	def getWeeklyVolume(symbol):
		return db.query( 
			"select week(time, 3) as week, year(time) as year, count(*) as message_count "
			"from messages_w_sentiment_v2 "
			"where date(time) between 20140101 and 20161231 "
			"and symbol = " + "'"+symbol+"' "
			"group by week,year "
			"order by year,week "
			)

	result = getWeeklyVolume(stock)
	dataset.freeze(result, format='csv', filename=stock+'messageVolume.csv')

	mvdf = pd.read_csv(stock+'messageVolume.csv')

	#get volume
	ydf = yahooDownloader.download(stock,1,1,2014,31,12,2016)

	vdf = ydf[['Volume']].copy()
	vdf['date'] = ydf.index

	kw = lambda x: x.isocalendar()[1]
	kw_year = lambda x: str(x.year) + ' - ' + str(x.isocalendar()[1])
	#grouped = vdf.groupby([vdf['date'].map(kw)], sort=False).agg({'Volume': 'sum'})
	grouped = vdf.groupby([vdf['date'].map(kw_year)], sort=False).agg({'Volume': 'sum'})

	mvdf = mvdf[:-1]


	#prepare plot
	x = mvdf['message_count']
	y = grouped['Volume']


	#regress
	slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
	r_x, r_y = zip(*((i, i*slope + intercept) for i in range(0,5000000,100000)))

	#plot
	p = figure (plot_width=400, plot_height=400)
	output_file("index.html")
	p.line(r_x, r_y, color="red")
	p.scatter(x, y, marker="square", color="blue")
	p.left[0].formatter.use_scientific = False
	p.xaxis.axis_label = 'Stocktwits Message Volume'
	p.yaxis.axis_label = 'Trading Volume'

	p.title.text = stock
	p.title.align = "center"
	p.title.text_font_size = "25px"
	pvalue_subtitle = "p-value: "+str(p_value)
	p.add_layout(Title(text=pvalue_subtitle, align="center"), "below")
	p.x_range = Range1d(0, x.max())
	p.y_range = Range1d(0, y.max())
	show(p)