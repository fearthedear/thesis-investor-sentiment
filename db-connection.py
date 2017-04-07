#!/usr/bin/python

#import dataset

#db = dataset.connect('mysql://majorshepard:vaporwavey@virg-stocktwits-sentiment.carho5gkg4wp.us-east-1.rds.amazonaws.com:3306/stocktwits_sentiment')
import sys; sys.dont_write_bytecode = True
import config
import mysql.connector

cnx = mysql.connector.connect(user=config.user, password=config.pw,
                              host=config.host,
                              database=config.database)

print 'connection established'
cnx.close()
