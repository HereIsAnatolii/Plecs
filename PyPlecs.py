class PyPlecs():
    def __init__(self,model,**kwargs):
        ''' model : str, user : str, version : float , localhost : int, path : str, SimTime : float'''
        import xmlrpc.client as xml
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        
        # set default input parameters
        defaultKwargs = { 'user': 'TCA1RNG', 'version': 4.8,'localhost':1080, 'path':'C://Anatolii//EMY-050//TCM','SimTime':0.02 }
        kwargs = { **defaultKwargs, **kwargs }
        
        # assign to the class variables
        self.plecs = xml.Server(f'http://localhost:{kwargs["localhost"]}/RPC2').plecs
        self.plecs_path = f'C://Users//{kwargs["user"]}//Documents//Plexim//PLECS {kwargs["version"]} (64 bit)//plecs.exe'
        self.model = kwargs['path']+f"//{model}"
        self.SimTime = kwargs['SimTime']
        self.params = {}
        self.df = pd.DataFrame()
        
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
            self.param2loop[param] = [f"{val}*{mul}" for val in np.linspace(kwargs['start'],kwargs['stop'],kwargs['steps'])]
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
        ''' SimTime : float, period : float, names : [str], Nouts : int, scopes : [str], LastValue : bool '''
        # set default input parameters
        defaultKwargs = { 'SimTime': self.SimTime, 'Nouts' : 1, 'LastValue':False}
        kwargs = { **defaultKwargs, **kwargs }
        
        self.SimTime = kwargs['SimTime']
        self.plecs.set(self.model,'TimeSpan',f'{self.SimTime}')
        self.means = pd.DataFrame()
        # update the parameters
        param_names = []
        for key,values in self.param2loop.items():
            param_names.append(key)
            
        if len(param_names) > 0:
            # run actual loop
            for i,val1 in enumerate(self.param2loop[param_names[0]]):
                print(f'Cycle {i}, {param_names[0]} = {val1:.3f} ')
                params[param_names[0]] = val1
                # run sub-loop if more than 1 loop parameters given
                # later - save csv and svg and plot
                if len(param_names) > 1:
                    for j,val2 in enumerate(self.param2loop[param_names[1]]):
                        params[param_names[1]] = val2
                        print(f'SubCycle {j}, {param_names[1]} = {val2} ')
                        params[param_names[1]] = val2
                        self.reset_params()
                        self.plecs.simulate(self.model)
                        # 1. save all subsims to csv + svg
                        # 2. find min,max, mean and rms of each result
                        # 3. save only the last values
                        
                else:
                    self.reset_params()
                    results = self.plecs.simulate(self.model)
                    if 'names' in kwargs:
                        self.df['t'] = results['Time']
                        self.means.loc[i,param_names[0]] = round(val1,3)
                        for k, name in enumerate(kwargs['names']):
                            self.df[name] = results['Values'][k]
                            msk = self.df['t'] > (self.df['t'].values[-1]-kwargs['period']) if 'period' in kwargs else self.df['t'] > 0
                            mean = (self.df.loc[msk,name].mean())
                            maxx = self.df.loc[msk,name].max()
                            rms = (self.df.loc[msk,name].pow(2).sum()/self.df[msk].shape[0])**0.5
                            
                            self.means.loc[i,name+' mean'] = mean
                            self.means.loc[i,name+' rms'] = rms
                            self.means.loc[i,name+' max'] = maxx
                    else:
                        for i in range(kwargs['Nouts']):
                            self.df[f'Res {i}'] = results['Values'][i]
                    self.df.to_csv(f"{self.model}-{param_names[0]}-{val1:.3f}.csv",index=False)
                    self.df = pd.DataFrame()
                    # 1. save all subsims to csv + svg
                    # 2. find min,max, mean and rms of each result
                    # 3. save only the last values
        else:
            # reset all the params and run a single simulation
            self.reset_params()
            results = self.plecs.simulate(self.model)

            # if 'names' defined as a list, the table gets the values from the list
            # otherwise the results will be saved as res 0, res 1, res 2 ...
            # if LastValue is True, only the last value will be saved
            if 'names' in kwargs:
                for i, name in enumerate(kwargs['names']):
                    self.df[name] = results['Values'][i][-1] if kwargs['LastValue'] else results['Values'][i]
            else:
                for i in range(kwargs['Nouts']):
                    self.df[f'Res {i}'] = results['Values'][i][-1] if kwargs['LastValue'] else results['Values'][i]
