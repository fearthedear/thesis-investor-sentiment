import gspread

import quickstart

credentials = quickstart.get_credentials()

gs = gspread.authorize(credentials)

gsheet = gs.open("Tests and regressions: Outline")

wsheet = gsheet.worksheet("REGS")

wsheet.update_acell('AA1', 'Christian Moms Against Dabbing')