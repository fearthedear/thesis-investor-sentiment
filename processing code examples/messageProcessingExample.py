import json
import dataset
import sys; sys.dont_write_bytecode = True
import config

#connection

#connect to aws
#db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.host+'/'+config.database)

#connect local
db = dataset.connect('mysql://root:root@localhost/thesis_test')

table = db['messages_w_sentiment']

#with open('messageExcerpt.json') as data_file:    
#   data = json.load(data_file)

stringjson = ""

with open('./stocktwits-archive/2016/01/split/xaa') as data_file:
    for line in data_file:
    	stringjson += line+','

stringjson = stringjson[:-1]

stringjson = "["+stringjson+"]"

messages = json.loads(stringjson)


def insertSentimentMessages(messages):
	for message in messages:
		if message['entities']['sentiment']:
			try:
				temp = dict(time=message['object']['postedTime'],approach=message['actor']['tradingStrategy']['approach'],holdingPeriod=message['actor']['tradingStrategy']['holdingPeriod'],experience=message['actor']['tradingStrategy']['experience'],symbol=message['entities']['symbols'][0]['symbol'],stocktwits_id=message['entities']['symbols'][0]['stocktwits_id'],exchange=message['entities']['symbols'][0]['exchange'],industry=message['entities']['symbols'][0]['industry'],sector=message['entities']['symbols'][0]['sector'],trending=message['entities']['symbols'][0]['trending'],price=message['entities']['symbols'][0]['price'],sentiment=message['entities']['sentiment']['basic'])
				table.insert(temp)
				print (str(temp)+" inserted")
			except:
				print('skipped')
		else:
			continue
