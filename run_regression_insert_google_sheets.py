import gspread

import quickstart
import runRegression_v2_programmatically

credentials = quickstart.get_credentials()

gs = gspread.authorize(credentials)

gsheet = gs.open("Tests and regressions: Outline")

wsheet = gsheet.worksheet("REGS")

cell_list = wsheet.findall("Python")

runRows = []
for cell in cell_list:
	runRows.append(cell.row)

# get symbol, value, aggregated, lag
regressThis = {}

for row in runRows:
	values_list = wsheet.row_values(row)
	temp = { "symbol": values_list[4], "value": values_list[5], "aggregated": values_list[6], "lag": values_list[13] }
	regressThis[row] = temp


i = 1
for r in regressThis.viewkeys():
	#run regression
	results = runRegression_v2_programmatically.runRegression(str(regressThis[r]['symbol']),str(regressThis[r]['value']),str(regressThis[r]['aggregated']),str(regressThis[r]['lag']))
	#insert result into gsheet
	wsheet.update_cell(r, 17, results['slope'])
	wsheet.update_cell(r, 18, results['p-value'])
	wsheet.update_cell(r, 19, results['r-squared'])

	print('done '+ str(i) + " / " + str(len(regressThis.viewkeys())) )
	i+=1



