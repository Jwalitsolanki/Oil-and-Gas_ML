# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import pandas as pd
import dlisio
dlisio.set_encodings(['latin1'])
import matplotlib.pyplot as plt
import numpy as np
import numpy.lib.recfunctions as rfn

filepath = r"C:/Users/Jwalit/Downloads/WL_RAW_GR-REMP_MWD_1.DLIS"

"""with dlisio.load(filepath) as file:
    for d in file:
        depth_channels = d.match('TDEP')
        for channel in depth_channels:
            print(channel.name)
            
with dlisio.load(filepath) as file:
    print(file.describe())
with dlisio.load(filepath) as file:
    for d in file:
        for fram in d.frames:
            print(fram.curves())
    
with dlisio.load(filepath) as file:
    for d in file:
        print(d.describe())
        for fram in d.frames:
            print(fram.describe())
            for channel in d.channels:
                print(channel.describe())
        
with dlisio.load(filepath) as file:
    for d in file:
        for origin in d.origins:
            print(origin.describe())"""

curves_L = []
curves_name = []
longs = []
unit = []
files_L = []
files_num = []
frames = []
frames_num = []
with dlisio.load(filepath) as file:
    for d in file:
        files_L.append(d)
        for fram in d.frames:
            frames.append(fram)
            for channel in d.channels:
                curves_name.append(channel.name)
                longs.append(channel.long_name)
                unit.append(channel.units)
                files_num.append(len(files_L))
                frames_num.append(len(frames))
                curves = channel.curves()
                curves_L.append(curves)
        
curve_index = pd.DataFrame(
{'Curve': curves_name,
'Long': longs,
'Unit': unit,
'Internal_File': files_num,
'Frame_Number': frames_num
})



import hvplot.pandas
import holoviews as hv
from holoviews import opts, streams
from holoviews.plotting.links import DataLink
hv.extension('bokeh', logo=None)

def df_column_uniquify(df):
    df_columns = df.columns
    new_columns = []
    for item in df_columns:
        counter = 0
        newitem = item
        while newitem in new_columns:
            counter += 1
            newitem = "{}_{}".format(item, counter)
        new_columns.append(newitem)
    df.columns = new_columns
    return df

curve_df = pd.DataFrame()
name_index = 0
for c in curves_L:
    name = curves_name[name_index]
    np.vstack(c)
    try:
        num_col = c.shape[1]
        col_name = [name] * num_col
        df = pd.DataFrame(data=c, columns=col_name)
        name_index = name_index + 1
        df = df_column_uniquify(df)
        curve_df = pd.concat([curve_df, df], axis=1)
    except:
        num_col = 0
        df = pd.DataFrame(data=c, columns=[name])
        name_index = name_index + 1
        curve_df = pd.concat([curve_df, df], axis=1)
        continue

curve_df = df_column_uniquify(curve_df)
curve_df['DEPTH_Calc_ft'] = curve_df.loc[:,'TDEP'] * 0.0083333 #0.1 inch/12 inches per foot
curve_df['DEPTH_ft'] = curve_df['DEPTH_Calc_ft']
curve_df = curve_df.set_index("DEPTH_Calc_ft")
curve_df.index.names = [None]
curve_df = curve_df.replace(-999.25,np.nan)
min_val = curve_df['DEPTH_ft'].min()
max_val = curve_df['DEPTH_ft'].max()
curve_list = list(curve_df.columns)
curve_list.remove('DEPTH_ft')

#print(curve_df.head())

def curve_plot(log, df, depthname):
  aplot = df.hvplot(x=depthname, y=log, invert=True, flip_yaxis=True, shared_axes=True,
                       height=600, width=300).opts(fontsize={'labels': 16,'xticks': 14, 'yticks': 14})
  return aplot;

plotlist = [curve_plot(x, df=curve_df, depthname='DEPTH_ft') for x in curve_list]
well_section = hv.Layout(plotlist).cols(len(curve_list))
hvplot.show(well_section)