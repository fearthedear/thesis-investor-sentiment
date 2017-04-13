import dataset
import json
import sys; sys.dont_write_bytecode = True
import config
import os

first_arg = sys.argv[1]

#connect to aws
#virg
#db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.hostvirg+'/'+config.database)
#frankfurt
db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.hostfrank+'/'+config.database)

#connect local
#db = dataset.connect('mysql://root:root@localhost/thesis_test')

#open, prepare, parse messages from json
def openFile(jsonFile):
	stringjson = ""
	with open(jsonFile) as data_file:
		for line in data_file:
			stringjson += line+','

	stringjson = stringjson[:-1]
	stringjson = "["+stringjson+"]"

	return json.loads(stringjson)


	
def upload(directory):
	for filename in os.listdir(directory):
		try:
			db.begin()
			message = openFile(directory+'/'+filename)
			for i in range(0,len(message)):
				if message[i]['entities']['sentiment']:
					try:
						temp = dict(containsSymbol=1,messageIdStocktwits=message[i]['id'],time=message[i]['object']['postedTime'],approach=message[i]['actor']['tradingStrategy']['approach'],holdingPeriod=message[i]['actor']['tradingStrategy']['holdingPeriod'],experience=message[i]['actor']['tradingStrategy']['experience'],symbol=message[i]['entities']['symbols'][0]['symbol'],stocktwits_id=message[i]['entities']['symbols'][0]['stocktwits_id'],exchange=message[i]['entities']['symbols'][0]['exchange'],industry=message[i]['entities']['symbols'][0]['industry'],sector=message[i]['entities']['symbols'][0]['sector'],trending=message[i]['entities']['symbols'][0]['trending'],price=message[i]['entities']['symbols'][0]['price'],sentiment=message[i]['entities']['sentiment']['basic'])
					except IndexError:
						temp = dict(containsSymbol=0,messageIdStocktwits=message[i]['id'],time=message[i]['object']['postedTime'],approach=message[i]['actor']['tradingStrategy']['approach'],holdingPeriod=message[i]['actor']['tradingStrategy']['holdingPeriod'],experience=message[i]['actor']['tradingStrategy']['experience'],sentiment=message[i]['entities']['sentiment']['basic'])
					
					db['messages_w_sentiment_v2'].insert(temp)
			db.commit()
			print ('inserted '+filename)
		except:
			db.rollback()
	print('done 100%')
	return

if __name__ == "__main__":
    upload(first_arg)

