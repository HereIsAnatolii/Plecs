from scipy.interpolate import interp1d, UnivariateSpline
import numpy as np

def spline(df,x,y,new_range):
    spline_function = UnivariateSpline(df[x], df[y])
    big_range = np.linspace(df.loc[0,x],df.loc[df.shape[0]-1,x],new_range)
    y_spline = spline_function(big_range)
    return big_range, y_spline

class MOSFET:
    def __init__(self):
        # Initialize the on_25 and off_25 members as lists of lists
        self.current = [0,1,3,5,10,20,30,40,50,60]
        self.on_25 = [[], [], []]
        self.off_25 = [[], [], []]
        self.on_150 = [[], [], []]
        self.off_150 = [[], [], []]
        self.RdsOn = 0
    def plot_curve(self, y_values):
        plt.plot(self.current,y_values)
    def interpolate(self, y_values, x):
        """
        Interpolate the y value corresponding to x given a list of x_values and y_values.
        
        :param x_values: List of x coordinates (must be sorted).
        :param y_values: List of y coordinates corresponding to x_values.
        :param x: The x value to interpolate.
        :return: The interpolated y value.
        """
        x_values = self.current
        if not x_values or not y_values or len(x_values) != len(y_values):
            raise ValueError("x_values and y_values must be non-empty and of the same length.")

        # Perform linear interpolation
        for i in range(1, len(x_values)):
            if x_values[i-1] <= x <= x_values[i]:
                # Linear interpolation formula: y = y0 + (x - x0) * (y1 - y0) / (x1 - x0)
                x0, y0 = x_values[i-1], y_values[i-1]
                x1, y1 = x_values[i], y_values[i]
                y = y0 + (x - x0) * (y1 - y0) / (x1 - x0)
                return y

        # If x is outside the range of x_values, raise an error or handle as needed
        raise ValueError("x value is outside the interpolation range.")
        
PMTX04 = MOSFET()
PMTW04 = MOSFET()
PMTX04.RdsOn = 62.2e-3
PMTW04.RdsOn = 38.7e-3

PMTX04.on_25[0] = [23.33,24.88,27.61,30.31,37.17,52.10,68.71,86.96,106.90,128.48] # 300 V
PMTX04.on_25[1] = [69.64,71.11,82.58,90.75,112.06,157.45,207.43,262.16,320.99,384.85] # 600 V
PMTX04.on_25[2] = [135.77,144.35,163.44,178.04,221.15,314.21,415.29,524.81,642.09,768.92] # 900 V

PMTX04.on_150[0] = [22.90,24.41,27.10,29.84,36.72,52.16,70.08,90.38,112.93,137.72] # 300 V
PMTX04.on_150[1] = [68.85,73.24,81.39,89.40,110.08,155.08,204.93,259.42,319.35,383.84] # 600 V
PMTX04.on_150[2] = [134.62,143.08,159.55,175.82,217.44,307.50,405.77,512.74,628.56,752.06] #900 V

PMTX04.off_25[0] = [8.12e-5,4.05e-4,5.94e-3,1.88e-2,9.98e-2,8.30e-1,4.51e0,1.30e1,2.54e1,4.08e1] # 300 V
PMTX04.off_25[1] = [8.11e-5,4.05e-4,5.94e-3,1.88e-2,9.9e-2,8.48e-1,1.07e1,3.41e1,6.32e1,9.63e1] # 600 V
PMTX04.off_25[2] = [8.11e-5,4.05e-4,5.94e-3,1.88e-2,9.99e-2,8.58e-1,2.39e1,7.27e1,1.3e2,1.92e2] # 900 V

PMTX04.off_150[0] =[0.000146,0.000778,0.011149,0.03475,0.169,1.211,5.792,15.47,28.97,45.51] # 300 V
PMTX04.off_150[1] =[0.000146,0.000778,0.011145,0.034737,0.1688,1.245,14.758,40.75,71.94,106.97] # 600 V
PMTX04.off_150[2] =[0.000146,0.000777,0.0111,0.03473,0.1687,1.274,32.57,84.81,144.47,209.26] # 900 V

PMTW04.on_25[0] = [23.33,24.88,27.61,30.31,37.17,52.10,68.71,86.96,106.90,128.48] # 200 V
PMTW04.on_25[1] = [69.64,71.11,82.58,90.75,112.06,157.45,207.43,262.16,320.99,384.85] # 400 V
PMTW04.on_25[2] = [135.77,144.35,163.44,178.04,221.15,314.21,415.29,524.81,642.09,768.92] # 600 V

PMTW04.on_150[0] = [] # 200 V
PMTW04.on_150[1] = [43.58,46.77,52.81,58.79,74.16,107.35,144.21,184.76,229.02,277.19] # 400 V
PMTW04.on_150[2] = [] # 600 V

PMTW04.off_25[0] = [8.12e-5,4.05e-4,5.94e-3,1.88e-2,9.98e-2,8.30e-1,4.51e0,1.30e1,2.54e1,4.08e1] # 200 V
PMTW04.off_25[1] = [8.11e-5,4.05e-4,5.94e-3,1.88e-2,9.9e-2,8.48e-1,1.07e1,3.41e1,6.32e1,9.63e1] # 400 V
PMTW04.off_25[2] = [8.11e-5,4.05e-4,5.94e-3,1.88e-2,9.99e-2,8.58e-1,2.39e1,7.27e1,1.3e2,1.92e2] # 600 V

PMTW04.off_150[0] =[] # 200 V
PMTW04.off_150[1] =[0.000434,0.000195,0.00585,0.024251,0.1475,2.4,18.06,39.97,65.57,94.33] # 400 V
PMTW04.off_150[2] =[] # 600 V
