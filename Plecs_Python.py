# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import xmlrpc.client as xml

# Change the working directory
os.chdir(r'D:\Work\Simulation\Plecs\T-Type')
# choose the simulation file
file_type = '.plecs'
model_name = 'CCM'

# connect plecs to python
plecs = xml.Server('http://localhost:1080/RPC2').plecs

plecs.load(model_name+file_type)

# change the simulation settings
plecs.set(model_name,'TimeSpan','0.5')

# initial model parameters
Vdc = 800
Vac = 230
fsw = 100e3
L = 330e-6
Cdc = 1280e-6
P = 3600

Imax = 3*P/Vdc*(3.0/2.0)**0.5
Rdc = Vdc**2/(Imax*Vac)
i = 0
Kp = L*fsw/3
Ki = 1e-4*fsw/3

init = ''
params = {'P' : P,'Cdc' : Cdc,'Vdc' : Vdc,'Vac' : Vac,
      'fsw' : fsw,'L' : L,'Cf' : Cf,'ESR' : 1e-4,
      'I_max' : Imax,'Rdc' : Rdc,'Run' : i,'Kp' : Kp, 'Ki' : Ki,'w' : 5}

# write the parameters into PLECS' Initialization Command 
for key,val in params.items():
    init += f'{key} = {val};\n'    
plecs.set(model_name,'InitializationCommands',init)

# Change Simulation mode 
sim_mode = 2 
# Number of simulation runs
Nmax = 20
match sim_mode:
    case 1:
        Power = np.linspace(100,3600,Nmax)
        plecs.set(model_name+'/Manual Switch','SwitchState','on')
        plecs.set(model_name+'/x1','CommentStatus','Active')
        plecs.set(model_name+'/x2','CommentStatus','CommentedOut')
    case 2:
        Power = np.linspace(3600,7200,Nmax)
        plecs.set(model_name+'/Manual Switch','SwitchState','off')
        plecs.set(model_name+'/x1','CommentStatus','CommentedOut')
        plecs.set(model_name+'/x2','CommentStatus','Active')

# Create the dataframe to store the results
df = pd.DataFrame()
df['P_arr'] = Power
init = ''

# Reset the scopes
plecs.scope(model_name+f'/x{sim_mode}/Power-Voltages','ClearTraces')
plecs.scope(model_name+f'/x{sim_mode}/Averaging','ClearTraces')

# Set up the plot figure
fig,p=plt.subplots(1,2)
fig.set_figwidth(15)

# Run simulations
for i,P in enumerate(Power):

    M = 2*Vac*(2)**0.5/Vdc
    Imax = 3*P/Vdc*(3.0/2.0)**0.5
    Rdc = Vdc**2/(Imax*Vac)
   
    params = {'P' : P,'Cdc' : Cdc,'Vdc' : Vdc,'Vac' : Vac,
          'fsw' : fsw,'L' : L,'Cf' : Cf,'ESR' : 1e-4,
          'I_max' : Imax,'Rdc' : Rdc,'Run' : i+1,'Kp' : Kp, 'Ki' : Ki,'w' : 5}
    init = ''
    for key,val in params.items():
        init += f'{key} = {val};\n'
    plecs.set(model_name,'InitializationCommands',init)

    results = plecs.simulate(model_name)
    sim_time = results['Time']
    waves = results['Values']
    plecs.scope(model_name+f'/x{sim_mode}/Power-Voltages','HoldTrace',f'P = {round(P,2)} W')
    plecs.scope(model_name+f'/x{sim_mode}/Averaging','HoldTrace',f'P = {round(P,2)} W')
    
    df.loc[i,'rms_h'] = waves[0][-1]
    df.loc[i,'rms_n']  = waves[1][-1]
    df.loc[i,'sw_rms_h']  = waves[2][-1]
    df.loc[i,'sw_rms_n']  = waves[3][-1]
    
    p[0].plot(sim_time,waves[6])
    p[0].set_xlim(0.42,0.5)

# Plot results
df.plot(ax=p[1],x='P_arr',y=['rms_h','rms_n'])
