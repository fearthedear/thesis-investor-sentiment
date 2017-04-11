#dataset requires mysqldb
import dataset
import config

#connect to aws
#db = dataset.connect('mysql://'+config.user+":"+config.pw+"@"+config.host+'/'+config.database)

#connect local
db = dataset.connect('mysql://root:root@localhost/thesis_test')

