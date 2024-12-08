classdef MatPlecs <handle
    properties
        path                % path to the simulation file
        model               % name of the model file
        type                % type of the simulation file
        proxy               % proxy connetion to plecs

        simStruct           % simulation parameters
        results             % structure with results
    end
    
    methods
        function obj = MatPlecs(varargin)
            % Constructor with varargin
            % Varargin parser with DEFAULT VALUES
            p = inputParser;
            addParameter(p,'path','C:/');               % Default search path
            addParameter(p,'model','notdefined');       % Default model name
            addParameter(p,'clc',true);                 % clear close all
            parse(p, varargin{:});

            if p.Results.clc == true
                clc; close all;
            end

            obj.path = p.Results.path;
            obj.model = p.Results.model;
            obj.type = '.plecs';

            % create cell array for SimStruct
            obj.simStruct = struct('ModelVars',struct('plecs',0));

            % SETUP NEW OBJECT
            disp('=================================================================================')
            fprintf('PLECS connection is established\nUsed directory -> %s,\nUsed simulation file -> %s\n',obj.path,obj.model);
        end
        function obj = addParam(obj,name,value)
            fprintf('Parameter changed->%s = %f\n',name,value);
            obj.simStruct.ModelVars.(name) = value;
        end
        function PlecsConnect(obj,varargin)
            % Establish connection with plecs model
            % Create JSON connection to PLECS with the timeout 300 seconds
            p = inputParser;
            addParameter(p,'host',1080);                 % localhost to connect
            addParameter(p,'timeout',100);               % Plot the output
            parse(p, varargin{:});

            host = p.Results.host;
            timeout = p.Results.timeout;
            url = "http://localhost:";
            obj.proxy = jsonrpc(strcat(url, num2str(host)), 'Timeout', timeout);

            obj.proxy.plecs.load([obj.path '/' obj.model obj.type]);
            fprintf('Connected to plecs at localhost->%d, Timeout->%d\n',1080,300);
        end

        function obj = loopsim(obj,param,start,stop,N,varargin)
            % variable arguments will be the names of output values
            p = inputParser;
            addParameter(p,'names',[]);                 % Names of the output values
            addParameter(p,'plot',true);                % Plot the output
            addParameter(p,'structure',NaN);            % Structure of the plots
            parse(p, varargin{:});
            
            names = p.Results.names;
            structure = p.Results.structure;
            to_plot = p.Results.plot;

            fprintf('%s will be simulated %d times\n',param,N);
            values = linspace(start,stop,N);
            for value = values
                obj.addParam(param,value);
                obj.simulate('names',names,'structure',structure,'plot',to_plot);
            end
            % Add here options like RMS, mean
        end
        function obj = simulate(obj,varargin)
            % variable arguments will be the names of output values
            p = inputParser;
            addParameter(p,'names',[]);                 % Names of the output values
            addParameter(p,'plot',true);                % Plot the output
            addParameter(p,'structure',NaN);            % Structure of the plots
            parse(p, varargin{:});
            
            names = ( ( (p.Results.names) ) );
            structure = p.Results.structure;
            to_plot = p.Results.plot;
            
            temp_results = obj.proxy.plecs.simulate(obj.model,obj.simStruct);

            N_outputs = size(temp_results.Values);
            fprintf('Simulation is finished, %d outputs recorded\n',int32( N_outputs(1)) ) ;
            obj.results = struct('time',temp_results.Time);

            % if names are not given
            if size(names) == 0
                for i=1:N_outputs
                    obj.results.( ['res_', num2str(i)] ) = temp_results.Values(i,:);
                end
            else
                for i=1:numel(names)
                    obj.results.( names{i} ) = temp_results.Values(i,:);
                end
            end
            if to_plot == true
                % set default structure
                if isnan(structure)
                    structure = ones(1,numel(names));
                end 
                obj.plot_results(names,structure);
            end

            % ADD ADDITIONAL METHOD AND VARARGIN TO CONFIGURE RMS/MEAN/MAX
            % OUTPUT POSSIBILITIES WHICH WILL BE SAVED IN A SEPARATE
        end
        function plot_results(obj,names,structure)
            % names = ["Vdc", "Idc", "Iac"]
            % structure = [1,1,1,3]
            test = struct2cell(obj.results);
            
            plots = names;
            n_plots = numel(structure);
            
            for i=1:n_plots
                % check whether the number of plots is higher than one
                if structure(i) > 1
                    subplot(n_plots,1,i)
                    for j=1:structure(i)
%                         fprintf("Current plot is %d\n",(i+j));
                        plot(test{1},test{i+j});
                        title(plots(i+j-1));
                        combinedTitle = join(plots(i:i+structure(i)-1), ', ');
                        hold on;
                    end 
                else
                    subplot(n_plots,1,i)
                    plot(test{1},test{i+1});
                    combinedTitle = plots(i);
                end
                title(combinedTitle);
                grid on;
            end

        end
        function obj = addPath(obj,filepath)
            % add file path if was not defined in the constructor
            obj.path = char(filepath);
            fprintf('Updated file path -> %s\n',obj.path);
        end
        function obj = addSimFile(obj,filename)
            % add new simulation file if was not defined in the constructor
            obj.model = char(filename);
            fprintf('Updated simulation file -> %s\n',obj.model);
        end
        % Define other methods here
    end
end
