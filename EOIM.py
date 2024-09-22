import math
from sympy import *
import numexpr
from sympy.core.evalf import evalf_float

from Error import Error


class EOIM:  # Error_of_indirect_measurements
    def __init__(self, allmsm, all_inst_err, formula):
        self.allmsm = allmsm
        self.all_inst_err = all_inst_err
        self.formula = formula

    def calculate(self):
        s = ''

    def mfs(self):  # method for sum
        er1 = Error(self.allmsm[0], self.all_inst_err[0])
        er2 = Error(self.allmsm[1], self.all_inst_err[0])
        a = er1.average_x()
        b = er2.average_x()
        a, b = symbols("a, b")
        dic = {a: er1.average_x(), b: er2.average_x()}
        z_average = eval(self.formula)  # formula(variant) = "a*b"
        s = 0
        symp_formula = sympify(self.formula)
        s += (diff(symp_formula, a).evalf(subs=dic) * er1.absolute_error()) ** 2
        s += (diff(symp_formula, b).evalf(subs=dic) * er2.absolute_error()) ** 2

        ind_absol_err = sqrt(s)
        return ind_absol_err


m = [[1, 1, 1, 1, 1], [2, 2, 2, 2, 2]]
ins = [1, 1]
er11 = Error(m[0], 1)
er22 = Error(m[1], 1)
eoim = EOIM(m, ins, "(a)*(b)")
print(eoim.mfs())
