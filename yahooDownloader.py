import pandas_datareader as pdr
from datetime import datetime

### INSERT VALUES ###
stock = 'FB'

startDay = 01
startMo = 01
startY = 2016

endDay = 31
endMo = 12
endY = 2016


def download(stock,startDay,startMo,startY,endDay,endMo,endY):
	history = pdr.get_data_yahoo(symbols=stock, start=datetime(startY, startMo, startDay), end=datetime(endY, endMo, endDay))
	return history


#this code runs the function if you want to download from the terminal
if __name__ == "__main__":
    download(stock,startDay,startMo,startY,endDay,endMo,endY)


