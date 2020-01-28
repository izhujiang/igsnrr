"""
landsat images post-process module
"""
# -*- coding: utf-8 -*-
import os
import pandas as pd
import re
from datetime import datetime, timedelta, date


def transpose(src_dir, dest_dir):
    if not os.path.exists(src_dir):
        print("Input dir not exist: ", src_dir)
        return
    if not os.path.exists(points_dir):
        os.makedirs(points_dir)

    data = {}
    xlsFiles = os.listdir(src_dir)
    for xls in xlsFiles:
        xls_file = os.path.join(src_dir, xls)
        if os.path.isfile(xls_file):
            m = re.search('\d{4}', xls)
            year = m.group(0)
            print(year)
            print("processing table: ", xls )
            df = pd.read_excel(xls_file, index_col="SampleID")
            dft = df.iloc[:,7:].transpose()
            
            dft['date'] = map(lambda x: x[5:], dft.index)
            dft['fdate'] = dft.index
            dft.index = dft['date']
            
            # dft_fk = dft.join(ts, how='outer')
            # dft_fk.to_csv(output_file, index=True)
            for sid, s in dft.iteritems():
                if sid == "date" or sid == "fdate":
                    continue
                if not data.has_key(sid):
                    data[sid] = pd.DataFrame({'date': ts}, index=dates)
                s.rename(year)
                dt = pd.DataFrame({year: s})
                data[sid] = data[sid].join(dt, how='outer')
    
    for k, v in data.items():
        fpath = os.path.join(dest_dir, k + ".xlsx")
        print("saving file: ", fpath)
        v.to_excel(fpath, index=False)
            
# main programme
begin = date(1996, 1, 1)
end = date(1997, 1, 1)
dates = []
for i in range((end-begin).days):
    day = begin +  timedelta(days=i)
    dates.append(day.strftime("%m%d"))

ts = pd.Series(dates, name="fake_date", index=dates)
# print(ts)

# change here: change the input and output dir 
tables_dir = "C:/ignrr/data/LT05/tables"
points_dir = "C:/ignrr/data/LT05/result"
transpose(tables_dir, points_dir)

tables_dir = "C:/ignrr/data/LT05/tables-qa"
points_dir = "C:/ignrr/data/LT05/result-qa"
transpose(tables_dir, points_dir)