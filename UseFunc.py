from Error import Error
from sympy import *


class UseFunc:

    def gaussian_function(self,ti, arr):
        err = Error(arr, 0)
        f = (1 / (err.dispersion_x()*sqrt(2*pi)))*exp(-((ti - err.average_x())**2)/(2*err.dispersion_x()**2))
        return f.evalf()
