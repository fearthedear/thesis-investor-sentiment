import sys; sys.dont_write_bytecode = True
import gspread

import quickstart
import runRegression_v2_programmatically
import pandas as pd

credentials = quickstart.get_credentials()

gs = gspread.authorize(credentials)

gsheet = gs.open("Tests and regressions: Outline")

wsheet = gsheet.worksheet("REGS")

results = pd.read_csv('all_results.csv')


for i in range(0, len(results)):
	row = int(results.iloc[i]['row'])
	slope = str(results.iloc[i]['slope'])
	pvalue = str(results.iloc[i]['p-value'] )
	rsquared = str(results.iloc[i]['r-squared'])
	wsheet.update_cell(row, 17, slope )
	wsheet.update_cell(row, 18, pvalue)
	wsheet.update_cell(row, 19, rsquared )