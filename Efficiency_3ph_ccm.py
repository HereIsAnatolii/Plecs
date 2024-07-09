# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 18:09:43 2024

@author: GBT B450M-S2H
"""

import os
import pandas as pd
from MOSFET import *
import matplotlib.pyplot as plt
from matplotlib import rcParams

os.chdir(r"G:\Work\4. BOSCH\EMY-050\Simulation\Plecs\T-Type")

# Variables
fsw = 70e3
new_range = 100

# Import data 
CCM = pd.read_csv("CCM_3ph.csv")

#
df = pd.DataFrame()
df['P_arr'],df['rms_H']     = spline(CCM,'P_arr','rms_h',new_range)
df['P_arr'],df['rms_N']     = spline(CCM,'P_arr','rms_n',new_range)
df['P_arr'],df['sw_rms_H']  = spline(CCM,'P_arr','sw_rms_h',new_range)
df['P_arr'],df['sw_rms_N']  = spline(CCM,'P_arr','sw_rms_n',new_range)

# update
CCM = pd.read_csv("CCM_3ph_interp.csv")
# Calculate the losses
CCM["Cond_H"] = CCM["rms_H"]**2 * PMTX04.RdsOn
CCM["Cond_N"] = CCM["rms_N"]**2 * PMTW04.RdsOn
CCM["Cond_T"] = CCM["Cond_H"]*6 + CCM["Cond_N"]*6

CCM["Sw_on_N"] =  [fsw * PMTW04.interpolate(PMTW04.on_150[1],val) * 1e-6 for val in CCM['sw_rms_N'].values]
CCM["Sw_off_N"] = [fsw * PMTW04.interpolate(PMTW04.off_150[1],val) * 1e-6 for val in CCM['sw_rms_N'].values]
CCM["Sw_on_H"] =  [fsw * PMTX04.interpolate(PMTX04.on_150[2],val) * 1e-6 for val in CCM['sw_rms_H'].values]
CCM["Sw_off_H"] = [fsw * PMTX04.interpolate(PMTX04.off_150[2],val) * 1e-6 for val in CCM['sw_rms_H'].values]

CCM["Sw_T"] = (CCM['Sw_on_N']*6 + CCM['Sw_off_N']*6 + CCM['Sw_on_H']*6 + CCM['Sw_off_H']*6)
CCM["Sw_T_H"] = CCM['Sw_on_H'] + CCM['Sw_off_H']
CCM["Sw_T_N"] = CCM['Sw_on_N'] + CCM['Sw_off_N']

CCM["Total_H"] = CCM["Cond_H"] + CCM["Sw_T_H"]
CCM["Total_N"] = CCM["Cond_N"] + CCM["Sw_T_N"]

# Plot everything
# Set the font properties
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.sans-serif'] = ['Bookman Old Style']  # Replace 'Arial' with your desired font
plt.rcParams['font.size'] = 17.5  # Example size

figwidth = 16.15
plt.style.use('bmh')
fig,p=plt.subplots(1,3)
fig.set_figwidth(figwidth)

p[0].set_title('Conduction losses per switch (W)')
p[1].set_title('Switching losses per switch (W)')
p[2].set_title('Total losses per switch (W)')

CCM.plot(ax=p[0],x="P_arr",y=["Cond_H","Cond_N"],label=["High","Neutral"],ylim=(0,10))
CCM.plot(ax=p[1],x="P_arr",y=["Sw_T_H","Sw_T_N"],label=["High","Neutral"],ylim=(0,10))
CCM.plot(ax=p[2],x="P_arr",y=["Total_H","Total_N"],label=["High","Neutral"],ylim=(0,20))
#CCM.plot(ax=p[3],x="P_arr",y=["Sw_off_H","Sw_off_N"],label=["High","Neutral"])

[ax.set_xlabel("Power (W)") for ax in p]
fig.savefig("conduction.svg")
