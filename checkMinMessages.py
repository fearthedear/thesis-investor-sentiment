import sys; sys.dont_write_bytecode = True
import dataset
import config

from warnings import filterwarnings
import MySQLdb as Database
filterwarnings('ignore', category = Database.Warning)

#connect aws rds frankfurt
db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.hostfrank+'/'+config.database)

numb = raw_input(" Show stocks with more than ??? messages --> ")
year = raw_input('For year --> ')

out = {}
for week in range(1,53):
	result = db.query(
			"select count(symbol), symbol from messages_w_sentiment_v2"
			" where week(time) = " + str(week) +
			" and year(time) = " + year +
			" group by symbol HAVING count(symbol) > " + numb
		)

	for row in result:
		try:
			out[row['symbol']] += 1
		except KeyError:
			out[row['symbol']] = 1

	print("done " + str(week) + " / 52" )

out = {k: v for k, v in out.iteritems() if v == 52 }
print(list(out.viewkeys()))