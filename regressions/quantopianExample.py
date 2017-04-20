from quantopian.interactive.data.psychsignal import stocktwits as dataset_st
from datetime import datetime
import numpy as np

fb = dataset_st[dataset_st.symbol == 'AAPL']
df_fb = odo(fb.sort('asof_date'), pd.DataFrame)
df_sorted = df_fb[(df_fb['asof_date'] >= datetime(2016,1,1,0,0,0)) & (df_fb['asof_date'] <= datetime(2016,1,7,23,59,59))]

bull_msg = sum(df_sorted.bull_scored_messages.values)
total_msg = sum(df_sorted.total_scanned_messages.values)
print(bull_msg)
print(total_msg)
print(bull_msg/total_msg)