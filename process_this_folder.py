import json
import dataset
import sys; sys.dont_write_bytecode = True
import config
import os

#getting argument when running from terminal
first_arg = sys.argv[1]

#connect to aws
db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.host+'/'+config.database)

#connect local
#db = dataset.connect('mysql://root:root@localhost/thesis_test')

table = db['messages_w_sentiment']

#open, prepare, parse messages from json
def openFile(jsonFile):
	stringjson = ""
	with open(jsonFile) as data_file:
		for line in data_file:
			stringjson += line+','

	stringjson = stringjson[:-1]
	stringjson = "["+stringjson+"]"

	return json.loads(stringjson)

def insertSentimentMessages(messages):
	for message in messages:
		if message['entities']['sentiment']:
			try:
				temp = dict(messageIdStocktwits=message['id'],time=message['object']['postedTime'],approach=message['actor']['tradingStrategy']['approach'],holdingPeriod=message['actor']['tradingStrategy']['holdingPeriod'],experience=message['actor']['tradingStrategy']['experience'],symbol=message['entities']['symbols'][0]['symbol'],stocktwits_id=message['entities']['symbols'][0]['stocktwits_id'],exchange=message['entities']['symbols'][0]['exchange'],industry=message['entities']['symbols'][0]['industry'],sector=message['entities']['symbols'][0]['sector'],trending=message['entities']['symbols'][0]['trending'],price=message['entities']['symbols'][0]['price'],sentiment=message['entities']['sentiment']['basic'])
				table.insert(temp)
				print (str(temp)+" inserted")
			except IndexError:
				temp = dict(messageIdStocktwits=message['id'],time=message['object']['postedTime'],approach=message['actor']['tradingStrategy']['approach'],holdingPeriod=message['actor']['tradingStrategy']['holdingPeriod'],experience=message['actor']['tradingStrategy']['experience'],sentiment=message['entities']['sentiment']['basic'])
				table.insert(temp)
				print ('inserted without symbol')
			except:
				with open('messagesFailedToUpload.txt', 'a') as error_file:
					error_file.write(message+'\n')
				print ('error! message written to error file')
		else:
			continue

def upload(directory):
	for filename in os.listdir(directory):
		insertSentimentMessages(openFile(directory+'/'+filename))
	return 'done'

if __name__ == "__main__":
    upload(first_arg)