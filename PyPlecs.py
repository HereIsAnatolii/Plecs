class PyPlecs():
    def __init__(self,model,**kwargs):
        ''' model : str, user : str, version : float , localhost : int, path : str, SimTime : float'''
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
        ''' SimTime : float, period : float, outputs : [str], name : str, Nouts : int, scopes : [str], LastValue : bool '''
        # set default input parameters
        defaultKwargs = { 'SimTime': self.SimTime, 'Nouts' : 1, 'LastValue':False, 'reset' : False}
        kwargs = { **defaultKwargs, **kwargs }
        
        self.SimTime = kwargs['SimTime']
        self.plecs.set(self.model,'TimeSpan',f'{self.SimTime}')
        if kwargs['reset']:
            self.means = pd.DataFrame()
            self.simTotal = 0
        
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
                    print(f'Cycle {i}, {param_names[0]} = {float(val1.split("*")[0]):.3f} ',end='; ')
                else:
                    isString = False
                    print(f'Cycle {i}, {param_names[0]} = {val1:.3f} ',end='; ')
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
                            for k, name in enumerate(kwargs['outputs']):
                                self.df[name] = results['Values'][k]
                                msk = self.df['t'] > (self.df['t'].values[-1]-kwargs['period']) if 'period' in kwargs else self.df['t'] > 0
                                mean = (self.df.loc[msk,name].mean())
                                maxx = self.df.loc[msk,name].max()
                                rms = (self.df.loc[msk,name].pow(2).sum()/self.df[msk].shape[0])**0.5

                                self.means.loc[i,name+' mean'] = mean
                                self.means.loc[i,name+' rms'] = rms
                                self.means.loc[i,name+' max'] = maxx
                                self.means.loc[i,name+' last'] = self.df[name].values[-1]
                        else:
                            for i in range(kwargs['Nouts']):
                                self.df[f'Res {i}'] = results['Values'][i]
                    
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
                        for k, name in enumerate(kwargs['outputs']):
                            self.df[name] = results['Values'][k]
                            msk = self.df['t'] > (self.df['t'].values[-1]-kwargs['period']) if 'period' in kwargs else self.df['t'] > 0
                            mean = (self.df.loc[msk,name].mean())
                            maxx = self.df.loc[msk,name].max()
                            rms = (self.df.loc[msk,name].pow(2).sum()/self.df[msk].shape[0])**0.5
                            
                            self.means.loc[self.simTotal,name+' mean'] = mean
                            self.means.loc[self.simTotal,name+' rms'] = rms
                            self.means.loc[self.simTotal,name+' max'] = maxx
                            self.means.loc[self.simTotal,name+' last'] = self.df[name].values[-1]
                    else:
                        for i in range(kwargs['Nouts']):
                            self.df[f'Res {i}'] = results['Values'][i]
                    
                    self.means[param_names[0]] = self.means[param_names[0]].astype('float') # error here
                    if isString==False:
                        self.df[msk].to_csv(f"{timenow}-{self.name}-{param_names[0]}-{val1:.3f}.zip",index=False)
                        self.files.loc[self.simTotal,'File'] = f"{timenow}-{self.name}-{param_names[0]}-{val1:.3f}.zip"
                        self.files.loc[self.simTotal,'Date'] = f"{timenow.split('-')[0]}" # %m.%d-%H.%M
                        self.files.loc[self.simTotal,'Time'] = f"{timenow.split('-')[1]}" # %m.%d-%H.%M
                    else:
                        self.df[msk].to_csv(f"{timenow}-{self.name}-{param_names[0]}-{float(val1.split('*')[0]):.3f}.zip",index=False)
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
