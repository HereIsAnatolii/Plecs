import tkinter as tk
from tkinter import ttk

# class should inherit from tk.Tk
class App(tk.Tk):
    def __init__(self,title,size):
        # ensure that the inheritance works properly
        super().__init__()
        self.size = {'x':size[0],'y':size[1]}
        self.title(title)
        self.geometry(f'{self.size["x"]}x{self.size["y"]}')
        self.minsize(self.size['x'],self.size['y'])
        
        # widgets
        self.menu = Block(self,title = "Modulation Index",value = 0.5, steps = (0.01,0.1), limits = (0, 1.15))
        self.menu2 = Block(self,title = "DC Voltage",value = 800, steps = (10,50), limits = (0, 1000))
        self.menu.pack(side=tk.LEFT)
        self.menu2.pack(side=tk.LEFT)
        # run
        self.mainloop()

# recreate ttk Frame method as a class
class Block(ttk.Frame):
    def __init__(self,parent,**kwargs):
    # create the main method with a parent
    # it is the same as calling the object the same
    # and the parent should be the window
        super().__init__(parent)
        self.args = kwargs
        self.create_block()
#        self.place(x = 0, y = 0)#, relwidth = 0.5, relheight = 1)
        
    def create_block(self):
        main_frame = ttk.Frame(self, borderwidth=5, relief="solid")
        title_frame = ttk.Frame(main_frame,
                               borderwidth=1, relief="solid")
        action_frame = ttk.Frame(main_frame)
        
        self.entry_var = tk.StringVar(value=self.args['value'])
        self.entry_var.trace_add("write", self.on_entry_change)
        label = ttk.Label(title_frame,text=self.args['title'])
        
        self.entry_var = tk.StringVar()
        self.entry_var.trace_add("write", self.on_entry_change)
        self.entry_var.set(f"{self.args['value']}")
        self.frame_entry = ttk.Entry(action_frame, textvariable=self.entry_var)
#        self.frame_entry.insert(0,self.args['value'])
        
        button_up = ttk.Button(action_frame,text='>',width=4,command=self.increase_small)
        button_dn = ttk.Button(action_frame,text='<',width=4,command=self.decrease_small)
        button_2dn = ttk.Button(action_frame,text='<<',width=4,command=self.decrease_big)
        button_2up = ttk.Button(action_frame,text='>>',width=4,command=self.increase_big)
        button_rst = ttk.Button(action_frame,text='RESET',command=self.reset)
        
        main_frame.pack()
        title_frame.pack(fill='x')
        label.pack()
        
        action_frame.pack(fill='x')
        self.frame_entry.pack(fill='x')
        button_rst.pack(side=tk.BOTTOM,fill='both')
        button_2dn.pack(side=tk.LEFT)
        button_dn.pack(side=tk.LEFT)
        button_2up.pack(side=tk.RIGHT)
        button_up.pack(side=tk.RIGHT)
        
        
    def on_entry_change(self, *args):
        # This method is called whenever the content of the entry widget changes
        print(f"Entry content changed to: {self.entry_var.get()}")
        
    def reset(self):
        self.modify_entry(operand='rst',value=self.args['value'],rounding=2)
    def decrease_small(self):
        self.modify_entry(operand='-',value=self.args['steps'][0],rounding=2)
    def increase_small(self):
        self.modify_entry(operand='+',value=self.args['steps'][0],rounding=2)
    def decrease_big(self):
        self.modify_entry(operand='-',value=self.args['steps'][1],rounding=2)
    def increase_big(self):
        self.modify_entry(operand='+',value=self.args['steps'][1],rounding=2)
        
    def modify_entry(self,operand='+',value=1,rounding=5):
        current_value = float(self.frame_entry.get())
        
        if operand == '+':
            new_value = round(current_value + value,rounding)
        elif operand == '-':
            new_value = round(current_value - value,rounding)
        elif operand == 'rst':
            new_value = self.args['value']
            
        if new_value > self.args['limits'][1]:
            new_value = self.args['limits'][1]
        elif new_value < self.args['limits'][0]:
            new_value = self.args['limits'][0]
        try:
            self.frame_entry.delete(0,tk.END)
            self.frame_entry.insert(0,new_value)
        except ValueError:
            self.frame_entry.insert(0,current_value)
            print('ValueError')
            
            
App(title='Test',size=(500,500))
