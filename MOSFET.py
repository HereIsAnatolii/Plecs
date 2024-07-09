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
