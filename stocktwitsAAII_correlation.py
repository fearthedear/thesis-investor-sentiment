import sys; sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import dataset 
import config
import datetime
from scipy import stats
from bokeh.plotting import *
from bokeh.models import *

# suppress mysqldb warnings
from warnings import filterwarnings
import MySQLdb as Database
filterwarnings('ignore', category = Database.Warning)

#connect aws rds frankfurt
db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.hostfrank+'/'+config.database)

#import csv, create AAII df
AAIIdf = pd.read_csv('AAII_sentiment.csv')

stdf = pd.DataFrame()

startDayList = []
endDayList = []

for i in range(0, len(AAIIdf)-1):
	endDayList.append(AAIIdf.iloc[i]['Date'])
	startDayList.append(AAIIdf.iloc[i+1]['Date'])


stdf['startday'] = pd.Series(startDayList)
stdf['endday'] = pd.Series(endDayList)


#get bullish ratio from stocktwits


# for i in range(0, len(stdf)):
# 	start = stdf.iloc[i]['startday']
# 	end = stdf.iloc[i]['endday']
# 	start = start.replace("-","")
# 	end = end.replace("-","")
# 	result = db.query(
# 		"select avg(sentimentBool) as bullish_percentage from messages_w_sentiment_v2 "
# 		"where date(time) between " + start +" and " + end 
# 		)
# 	for row in result:
# 		bp_list.append(row['bullish_percentage'].to_eng_string())
bp_list = []
bplist = ['0.8137', '0.8298', '0.8385', '0.8432', '0.8389', '0.8223', '0.8338', '0.8039', '0.8011', '0.8208', '0.8240', '0.8061', '0.8184', '0.8323', '0.8180', '0.8198', '0.8417', '0.8247', '0.8401', '0.8486', '0.8529', '0.8493', '0.8306', '0.8187', '0.8361', '0.8323', '0.8138', '0.8421', '0.8334', '0.8575', '0.8434', '0.8366', '0.8124', '0.7758', '0.7821', '0.7908', '0.8140', '0.8127', '0.8037', '0.8113', '0.8140', '0.8187', '0.8275', '0.8085', '0.7692', '0.7532', '0.7064', '0.7610', '0.7623', '0.7099', '0.7320', '0.7636', '0.8190', '0.8247', '0.8192', '0.8050', '0.8298', '0.8112', '0.7602', '0.7766', '0.7896', '0.7991', '0.7766', '0.7784', '0.7668', '0.7156', '0.7556', '0.7609', '0.7182', '0.7684', '0.7079', '0.7743', '0.7724', '0.7667', '0.7908', '0.7998', '0.8102', '0.7656', '0.7752', '0.8227', '0.8191', '0.8280', '0.8166', '0.8281', '0.8209', '0.8041', '0.8022', '0.8197', '0.8300', '0.8358', '0.8248', '0.8124', '0.8143', '0.8258', '0.8031', '0.8221', '0.8370', '0.8439', '0.8222', '0.8267', '0.8404', '0.8012', '0.7996', '0.8165', '0.8337', '0.8268', '0.7751', '0.7736', '0.7826', '0.8314', '0.8213', '0.8358', '0.8127', '0.7972', '0.8138', '0.7808', '0.7831', '0.7845', '0.7737', '0.8036', '0.8245', '0.8333', '0.8373', '0.8353', '0.8289', '0.8074', '0.8101', '0.8392', '0.8270', '0.8199', '0.8625', '0.8567', '0.8436', '0.8377', '0.8103', '0.8286', '0.7917', '0.7831', '0.7550', '0.7754', '0.8249', '0.7568', '0.7945', '0.8520', '0.8192', '0.8264', '0.8440', '0.8688', '0.8497', '0.8374', '0.8424', '0.7847', '0.8166', '0.8515', '0.8474', '0.8160']
for i in bplist:
	bp_list.append(float(i))



stdf['bullish_percentage'] = pd.Series(bp_list)

AAIIdf = AAIIdf[:-1]
# regression

x = stdf['bullish_percentage']
y = AAIIdf['Bullish']

print(x)
print(y)

slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
pvalue = "p-value: "+ str(p_value)
rsquared = "r-squared: "+ str(r_value**2)
slopep = "slope: " + str(slope)
r_x, r_y = zip(*((i, i*slope + intercept) for i in range(-15,15)))

p = figure (plot_width=400, plot_height=400)
output_file("index.html")
p.line(r_x, r_y, color="red")
p.scatter(x, y, marker="square", color="blue")
p.title.text = "AAII and Stocktwits Sentiment"
p.title.align = "center"
p.title.text_font_size = "25px"
p.xaxis.axis_label = 'Stocktwits Sentiment'
p.yaxis.axis_label = 'AAII Sentiment'
p.x_range = Range1d(x.min(), x.max()) 
p.y_range = Range1d(y.min(), y.max())
show(p)

print(pvalue)
print(rsquared)
print(slopep)
