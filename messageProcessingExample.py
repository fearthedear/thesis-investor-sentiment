import json
import dataset
import sys; sys.dont_write_bytecode = True
import config

#connection

#connect to aws
db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.host+'/'+config.database)

#connect local
#db = dataset.connect('mysql://root:root@localhost/thesis_test')

table = db['messages_w_sentiment']

#with open('messageExcerpt.json') as data_file:    
#   data = json.load(data_file)

stringjson = ""

with open('stocktwits_messages_2017_apr_01__4d17.json') as data_file:
    for line in data_file:
    	stringjson += line+','

stringjson = stringjson[:-1]

stringjson = "["+stringjson+"]"

messages = json.loads(stringjson)
#etc

for message in messages:
	if message['entities']['sentiment']:
		try:
			temp = dict(time=message['object']['postedTime'],approach=message['actor']['tradingStrategy']['approach'],holdingPeriod=message['actor']['tradingStrategy']['holdingPeriod'],experience=message['actor']['tradingStrategy']['experience'],symbol=message['entities']['symbols'][0]['symbol'],stocktwits_id=message['entities']['symbols'][0]['stocktwits_id'],exchange=message['entities']['symbols'][0]['exchange'],industry=message['entities']['symbols'][0]['industry'],sector=message['entities']['symbols'][0]['sector'],trending=message['entities']['symbols'][0]['trending'],price=message['entities']['symbols'][0]['price'],sentiment=message['entities']['sentiment']['basic'])
			table.insert(temp)
			print (str(temp)+" inserted")
		except:
			print('skipped: '+str(message))
	else:
		continue


print('done')