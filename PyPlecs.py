class PyPlecs():
    def __init__(self,model,**kwargs):
        ''' model : str, user : str, version : float , localhost : int, path : str, SimTime : float, params'''
        import xmlrpc.client as xml
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        
        # set default input parameters
        defaultKwargs = { 'user': 'Anatolii', 'version': 4.8,'localhost':1080, 'path':'C://Anatolii//','SimTime':0.02 }
        kwargs = { **defaultKwargs, **kwargs }
        
        # assign to the class variables
        self.plecs = xml.Server(f'http://localhost:{kwargs["localhost"]}/RPC2').plecs
        self.plecs_path = f'C://Users//{kwargs["user"]}//Documents//Plexim//PLECS {kwargs["version"]} (64 bit)//plecs.exe'
#        self.model = kwargs['path']+f"//{model}"
        if 'path' in kwargs:
            os.chdir(kwargs['path']) 
    
        self.model = model
        self.SimTime = kwargs['SimTime']
        self.params = {}
        self.df = pd.DataFrame()
        self.means = pd.DataFrame()
        self.files = pd.DataFrame()
        self.simTotal = 0
        # initially the number of parametric loops is 0
        # it should be increased every time self.setLoop is used
        self.loop = 0
        self.param2loop = dict()
        plt.style.use('bmh')
        
        # set params
        if 'params' in kwargs:
            self.add_params(params=kwargs['params'])
        
    def add_params(self,**kwargs):
        ''' params : list, values : list, csv : str, paradict : dictionary  '''
        # the parameters can be imported using two separate lists: params and values,
        #                                                          dictionaries or csv (not implemented)
        if 'params' in kwargs and isinstance(kwargs['params'],dict):
            self.params = kwargs['params']
        elif 'params' in kwargs and 'values' in kwargs and isinstance(kwargs['params'],list) and isinstance(kwargs['values'],list):
            for param, value in zip(kwargs['params'], kwargs['values']):
                print(param,end = ' = ')
                print(value)
                self.params[param] = value
        elif 'csv' in kwargs:
            print('csv')
        else:
            print('The parameters are not provided')
    def setLoop(self,param, **kwargs):
        ''' used to set a certain parameter for looped simulation
            param : str, start : float, stop : float, steps : float, mul=1 : float'''
        # set default input parameters
        defaultKwargs = { 'mul': 1}
        kwargs = { **defaultKwargs, **kwargs }
        # increase the number of loops
        if kwargs['mul'] != 1:
            # make a list of strings like 1*1e-6 for a better readability
            self.param2loop[param] = [f"{val}*{kwargs['mul']}" for val in np.linspace(kwargs['start'],kwargs['stop'],kwargs['steps'])]
        else:
            self.param2loop[param] = np.linspace(kwargs['start'],kwargs['stop'],kwargs['steps'])
    def reset_params(self):
        # reset the parameters before updating them
        init = ''
        self.plecs.set(self.model,'InitializationCommands',init)
        # write new parameters
        for key,val in self.params.items():
            init += f'{key} = {val};\n'
        self.plecs.set(self.model,'InitializationCommands',init)
        
    def simulate(self,**kwargs):
        ''' SimTime : float, period : float, outputs : [str], name : str, Nouts : int, scopes : [str], mean, max, rst, eval : ('name','eq') '''
        # set default input parameters
        defaultKwargs = { 'SimTime': self.SimTime, 'Nouts' : 1, 'reset' : False, 'mean' : True, 'max' : True, 'rms' : True}
        kwargs = { **defaultKwargs, **kwargs }
        
        self.SimTime = kwargs['SimTime']
        self.plecs.set(self.model,'TimeSpan',f'{self.SimTime}')
        if kwargs['reset']:
            self.means = pd.DataFrame()
            self.simTotal = 0
        # unpack the outputs
        # make number of plots depending on the size
        if 'outputs' in kwargs:
            outputs = kwargs['outputs']
            N_plots = len(outputs)
            N_outputs = []
            for i,value in enumerate(outputs):
                if isinstance(value,list):
                    # unpack the array and attach each value to the previous array
                    for sub_value in value:
                        N_outputs.append(sub_value)
                else:
                    # attache the value as it is to the previous array
                    N_outputs.append(value)

        # assign file name
        self.name = kwargs['name'] if 'name' in kwargs else self.model
        
        # check in the current time
        timenow = datetime.datetime.now().strftime("%m.%d-%H.%M")
        
        # update the parameters
        param_names = []
        for key,values in self.param2loop.items():
            param_names.append(key)
            
        if len(param_names) > 0:
            # run actual loop
            for i,val1 in enumerate(self.param2loop[param_names[0]]):
                if isinstance(val1,str):
                    isString = True
                    print(f'Cycle {i}, {param_names[0]} = {float(val1.split("*")[0]):.3f}',end='; ')
                else:
                    isString = False
                    print(f'Cycle {i}, {param_names[0]} = {val1:.3f}',end='; ')
                params[param_names[0]] = val1
                params['i'] = i
                # run sub-loop if more than 1 loop parameters given
                # later - save csv and svg and plot
                if len(param_names) > 1:
                    for j,val2 in enumerate(self.param2loop[param_names[1]]):
                        params[param_names[1]] = val2
                        print(f'SubCycle {j}, {param_names[1]} = {val2} ')
                        params[param_names[1]] = val2
                        self.reset_params()
                        self.plecs.simulate(self.model)
                        if 'outputs' in kwargs:
                            self.df['t'] = results['Time']
                            # put the value as float inside the table
                            if isString:
                                self.means.loc[i,param_names[0]] = float(val1.split('*')[0])
                            else:
                                self.means.loc[i,param_names[0]] = val1
                            for k, name in enumerate(N_outputs):
                                self.df[name] = results['Values'][k]
                                msk = self.df['t'] > (self.df['t'].values[-1]-kwargs['period']) if 'period' in kwargs else self.df['t'] > 0
                                mean = (self.df.loc[msk,name].mean())
                                maxx = self.df.loc[msk,name].max()
                                rms = (self.df.loc[msk,name].pow(2).sum()/self.df[msk].shape[0])**0.5
                                
                                if kwargs.pop('mean') == True:
                                    self.means.loc[i,name+'_mean'] = mean
                                if kwargs.pop('rms') == True:
                                    self.means.loc[i,name+'_rms'] = rms
                                if kwargs.pop('max') == True:
                                    self.means.loc[i,name+'_max'] = maxx
                                if kwargs.pop('last') == True:
                                    self.means.loc[i,name+'_last'] = self.df[name].values[-1]
                        else:
                            for ii in range(kwargs['Nouts']):
                                self.df[f'Res {ii}'] = results['Values'][ii]
                    
                    self.means[param_names[0]] = self.means[param_names[0]].astype('float')
                    if isString==False:
                        self.df[msk].to_csv(f"{timenow}-{self.name}-{param_names[0]}-{val1:.3f}.zip",index=False)
                        self.files['File'] = f"{timenow}-{self.name}-{param_names[0]}-{val1:.3f}.zip"
                        self.files['Date'] = f"{timenow.split('-')[0]}" # %m.%d-%H.%M
                        self.files['Time'] = f"{timenow.split('-')[1]}" # %m.%d-%H.%M
                    else:
                        self.df[msk].to_csv(f"{timenow}-{self.name}-{param_names[0]}-{float(val1.split('*')[0]):.3f}.zip",index=False)
                        self.files['File'] = f"{timenow}-{self.name}-{param_names[0]}-{float(val1.split('*')[0]):.3f}.zip"
                        self.files['Date'] = f"{timenow.split('-')[0]}" # %m.%d-%H.%M
                        self.files['Time'] = f"{timenow.split('-')[1]}" # %m.%d-%H.%M
                        
                    if 'eval' in kwargs:
                        row, eq = kwargs.pop('eval')
                        try:
                            self.means[row] = self.means.eval(eq)
                        except:
                            print('no spaces are allowed')
                    if kwargs.pop('reset') == True:
                        self.df = pd.DataFrame()
                    
                        # 1. save all subsims to csv + svg
                        # 2. find min,max, mean and rms of each result
                        # 3. save only the last values
                        
                else:
                    self.reset_params()
                    results = self.plecs.simulate(self.model)
                    if 'outputs' in kwargs:
                        self.df['t'] = results['Time']
                        # put the value as float inside the table
                        if isString:
                            self.means.loc[self.simTotal,param_names[0]] = float(val1.split('*')[0])
                        else:
                            self.means.loc[self.simTotal,param_names[0]] = val1
                        for k, name in enumerate(N_outputs):
                            self.df[name] = results['Values'][k]
                            msk = self.df['t'] > (self.df['t'].values[-1]-kwargs['period']) if 'period' in kwargs else self.df['t'] > 0
                            
                            mean = (self.df.loc[msk,name].mean())
                            maxx = self.df.loc[msk,name].max()
                            rms = (self.df.loc[msk,name].pow(2).sum()/self.df[msk].shape[0])**0.5

                            if kwargs.pop('mean') == True:
                                self.means.loc[i,name+'_mean'] = mean
                            if kwargs.pop('rms') == True:
                                self.means.loc[i,name+'_rms'] = rms
                            if kwargs.pop('max') == True:
                                self.means.loc[i,name+'_max'] = maxx
                            if kwargs.pop('last') == True:
                                self.means.loc[i,name+'_last'] = self.df[name].values[-1]
                    else:
                        for i in range(kwargs['Nouts']):
                            self.df[f'Res {i}'] = results['Values'][i]
                    
                    self.means[param_names[0]] = self.means[param_names[0]].astype('float') # error here
                    if isString==False:
                        # save a single simulation into csv
                        self.df[msk].to_csv(f"{timenow}-{self.name}-{param_names[0]}-{val1:.3f}.zip",index=False)
                        
                        fig, p = plt.subplots(len(kwargs['outputs']),sharex=True)
                        fig.set_figheight(len(kwargs['outputs'])*3)
                        
                        for k, name in enumerate(kwargs['outputs']):
                            self.df[msk].plot(ax=p[k],x='t',y=name)
                        
                        fig.savefig(f"{timenow}-{self.name}-{param_names[0]}-{val1:.3f}.svg")
                        fig.savefig(f"{timenow}-{self.name}-{param_names[0]}-{val1:.3f}.png",dpi=500)
                        fig.clf() # do not show the plot
                        plt.close()
                        
                        self.files.loc[self.simTotal,'File'] = f"{timenow}-{self.name}-{param_names[0]}-{val1:.3f}.zip"
                        self.files.loc[self.simTotal,'Date'] = f"{timenow.split('-')[0]}" # %m.%d-%H.%M
                        self.files.loc[self.simTotal,'Time'] = f"{timenow.split('-')[1]}" # %m.%d-%H.%M
                    else:
                        self.df[msk].to_csv(f"{timenow}-{self.name}-{param_names[0]}-{float(val1.split('*')[0]):.3f}.zip",index=False)
                        
                        fig, p = plt.subplots(len(kwargs['outputs']),sharex=True)
                        fig.set_figheight(len(kwargs['outputs'])*3)
                        for k, name in enumerate(kwargs['outputs']):
                            self.df[msk].plot(ax=p[k],x='t',y=name)
#                            p[k].text(self.df['t'].values[-1]*1.25, 0, f'RMS = {rms}\nMAX = {maxx}',ha='center', va='center', fontsize=12,bbox=dict(facecolor='white', edgecolor='black'))
                            
                        fig.savefig(f"{timenow}-{self.name}-{param_names[0]}-{float(val1.split('*')[0]):.3f}.svg")
                        fig.savefig(f"{timenow}-{self.name}-{param_names[0]}-{float(val1.split('*')[0]):.3f}.png",dpi=500)
                        fig.clf() # do not show the plot
                        plt.close()
                        
                        self.files.loc[self.simTotal,'File'] = f"{timenow}-{self.name}-{param_names[0]}-{float(val1.split('*')[0]):.3f}.zip"
                        self.files.loc[self.simTotal,'Date'] = f"{timenow.split('-')[0]}" # %m.%d-%H.%M
                        self.files.loc[self.simTotal,'Time'] = f"{timenow.split('-')[1]}" # %m.%d-%H.%M
                    
                    self.df = pd.DataFrame()
                    # 1. save all subsims to csv + svg
                    # 2. find min,max, mean and rms of each result
                    # 3. save only the last values
                self.simTotal += 1
            if isString:
                self.means.to_csv(f"{timenow}-{self.name}-means-{param_names[0]}={float(self.param2loop[param_names[0]][0].split('*')[0]):.3f}--{float(self.param2loop[param_names[0]][-1].split('*')[0]):.3f}.csv",index=False)
                self.files.to_csv(f"{timenow}-{self.name}-files-{param_names[0]}={float(self.param2loop[param_names[0]][0].split('*')[0]):.3f}--{float(self.param2loop[param_names[0]][-1].split('*')[0]):.3f}.csv",index=False)
            else:
                self.means.to_csv(f"{timenow}-{self.name}-means-{param_names[0]}={self.param2loop[param_names[0]][0]}--{self.param2loop[param_names[0]][-1]}.csv",index=False)
                self.files.to_csv(f"{timenow}-{self.name}-files-{param_names[0]}={self.param2loop[param_names[0]][0]}--{self.param2loop[param_names[0]][-1]}.csv",index=False)
        else:
            # reset all the params and run a single simulation
            self.reset_params()
            results = self.plecs.simulate(self.model)

            # if 'names' defined as a list, the table gets the values from the list
            # otherwise the results will be saved as res 0, res 1, res 2 ...
            # if LastValue is True, only the last value will be saved
            if 'outputs' in kwargs:
                for i, name in enumerate(kwargs['outputs']):
                    self.df[name] = results['Values'][i][-1] if kwargs['LastValue'] else results['Values'][i]
            else:
                for i in range(kwargs['Nouts']):
                    self.df[f'Res {i}'] = results['Values'][i][-1] if kwargs['LastValue'] else results['Values'][i]
                    
    def SimOne(self,**kwargs):
        ''' SimTime : float, period : float, outputs : [str], name : str, plot_first : int, scopes : [str], save_csv '''
        # set default input parameters
        defaultKwargs = { 'SimTime': self.SimTime, 'reset' : False, 'save_csv' : True, 'rms' : True, 'max' : True, 'mean' : True, 'last':True}
        kwargs = { **defaultKwargs, **kwargs }
        
        self.SimTime = kwargs['SimTime']
        self.plecs.set(self.model,'TimeSpan',f'{self.SimTime}')
        if kwargs['reset']:
            self.means = pd.DataFrame()
            self.simTotal = 0
        # unpack the outputs
        # make number of plots depending on the size
        if 'outputs' in kwargs:
            outputs = kwargs['outputs']
            N_plots = len(outputs)
            N_outputs = []
            for i, value in enumerate(outputs):
                if isinstance(value,list):
                    # unpack the array and attach each value to the previous array
                    for sub_value in value:
                        N_outputs.append(sub_value)
                else:
                    # attache the value as it is to the previous array
                    N_outputs.append(value)

        # assign file name
        self.name = kwargs['name'] if 'name' in kwargs else self.model
        
        # check in the current time
        timenow = datetime.datetime.now().strftime("%m.%d-%H.%M")
        
        # reset all params before running the simulation
        self.reset_params()
        results = self.plecs.simulate(self.model)
        
        self.df['t'] = results['Time']
        
        # assign each individual name in the DF 
        for k, name in enumerate(N_outputs):
            self.df[name] = results['Values'][k]
            msk = self.df['t'] > (self.df['t'].values[-1]-kwargs['period']) if 'period' in kwargs else self.df['t'] > 0

            mean = (self.df.loc[msk,name].mean())
            maxx = self.df.loc[msk,name].max()
            rms = (self.df.loc[msk,name].pow(2).sum()/self.df[msk].shape[0])**0.5

            if kwargs['mean'] == True:
                self.means.loc[self.simTotal,name+'_mean'] = mean
            if kwargs['rms'] == True:
                self.means.loc[self.simTotal,name+'_rms'] = rms
            if kwargs['max'] == True:
                self.means.loc[self.simTotal,name+'_max'] = maxx
            if kwargs['last'] == True:
                self.means.loc[self.simTotal,name+'_last'] = self.df[name].values[-1]
        
        # save a single simulation into csv
        if kwargs['save_csv'] == True:
            self.df[msk].to_csv(f"{timenow}-{self.name}_{self.simTotal}.zip",index=False)

        # if plot is not given, plot everything
        if 'plot_first' in kwargs:
            fig, p = plt.subplots(kwargs['plot_first'],sharex=True)
            fig.set_figheight(kwargs['plot_first']*3)
            
            for k, name in enumerate(kwargs['outputs'][:kwargs['plot_first']]):
                self.df[msk].plot(ax=p[k],x='t',y=name)
                
        else:
            fig, p = plt.subplots(len(kwargs['outputs']),sharex=True)
            fig.set_figheight(len(kwargs['outputs'])*3)

            for k, name in enumerate(kwargs['outputs']):
                self.df[msk].plot(ax=p[k],x='t',y=name)
        
        if 'eval' in kwargs:
            row, eq = kwargs.pop('eval')
            try:
                self.means[row] = self.means.eval(eq)
            except:
                print('no spaces are allowed')
            
        p[0].set_ylim(-35,35)
        self.df = pd.DataFrame()
        fig.savefig(f"{timenow}-{self.name}_{self.simTotal}.svg")
        fig.savefig(f"{timenow}-{self.name}_{self.simTotal}.png",dpi=500)
        fig.clf() # do not show the plot
        plt.close()
        self.simTotal += 1
        
    def SaveCSV(self,**kwargs):
        ''' outputs : bool, means : bool, files : bool, timestamp : bool, name : str, period : float '''
        # set default input parameters
        defaultKwargs = { 'outputs': True, 'means' : True, 'files' : True, 'timestamp' : True}
        kwargs = { **defaultKwargs, **kwargs }
        
        if 'name' in kwargs:
            self.name = kwargs['name'] 
            
        if kwargs['timestamp'] == True:
            # check in the current time
            timenow = datetime.datetime.now().strftime("%m.%d-%H.%M")
            timenow += '-'
        else:
            timenow = ''
        if kwargs['outputs'] == True:
            msk = self.df['t'] > (self.df['t'].values[-1]-kwargs['period']) if 'period' in kwargs else self.df['t'] > 0
            self.df[msk].to_csv(f"{timenow}{self.name}.zip",index=False)
        if kwargs['means'] == True:
            self.means.to_csv(f"{timenow}{self.name}-means.csv",index=False)
        if kwargs['means'] == True:
            self.files.to_csv(f"{timenow}{self.name}-files.csv",index=False)
