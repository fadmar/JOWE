from Error import Error
from sympy import *


class UseFunc:
    def __init__(self, arr):
        self.arr = arr

    def gaussian_function(self,ti):
        err = Error(self.arr, 0)
        f = (1 / (err.dispersion_x()*sqrt(2*pi)))*exp(-((ti - err.average_x())**2)/(2*err.dispersion_x()**2))
        return f.evalf()
