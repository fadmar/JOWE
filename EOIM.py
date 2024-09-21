import math
from sympy import *


class EOIM:  # Error_of_indirect_measurements
    def __init__(self, arr, formula):
        self.arr = arr
        self.formula = formula
    def calculate(self):
        s = ''

    def mfs(self):  # method for sum
        a =1