import math
from sympy import *
import numexpr

from Error import Error


class EOIM:  # Error_of_indirect_measurements
    def __init__(self, arr, formula):   #formula = "x[0]*x[1]**(-2)"
        self.arr = arr
        self.formula = formula

    def calculate(self):
        s = ''

    def mfs(self, arr_of_variable):  # method for sum
        x = arr_of_variable
        z = eval(self.formula)
        return z
m = [[1,1,1,1,1],[2,2,2,2,2]]
er1 = Error([1,1,1,1,1], 1)
er2 = Error([2,2,2,2,2], 1)
eoim = EOIM(m,"x[0]*x[1]**(-2)" )
print(eoim.mfs([er1.average_x(),er2.average_x()]))