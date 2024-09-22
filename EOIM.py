from sympy import *
from Error import Error


class EOIM:  # Error_of_indirect_measurements
    def __init__(self, allmsm, all_inst_err, formula):
        self.allmsm = allmsm
        self.all_inst_err = all_inst_err
        self.formula = formula

    def mth(self, meth, err):  # method for sum
        er1 = Error(self.allmsm[0], self.all_inst_err[0])
        er2 = Error(self.allmsm[1], self.all_inst_err[1])
        er3 = Error(self.allmsm[2], self.all_inst_err[2])
        er4 = Error(self.allmsm[3], self.all_inst_err[3])
        er5 = Error(self.allmsm[4], self.all_inst_err[4])
        er6 = Error(self.allmsm[5], self.all_inst_err[5])
        er7 = Error(self.allmsm[6], self.all_inst_err[6])
        er8 = Error(self.allmsm[7], self.all_inst_err[7])
        er9 = Error(self.allmsm[8], self.all_inst_err[8])
        er10 = Error(self.allmsm[9], self.all_inst_err[9])
        a, b, c, d, e, f, g, h, i, j = symbols("a, b, c, d, e, f, g, h, i, j")
        dic = {a: er1.average_x(), b: er2.average_x(), c: er3.average_x(), d: er4.average_x(), e: er5.average_x(),
               f: er6.average_x(), g: er7.average_x(), h: er8.average_x(), i: er9.average_x(), j: er10.average_x()}
        symp_formula = sympify(self.formula)
        z_average = symp_formula.evalf(subs=dic)

        def mfs():
            s = 0
            s += (diff(symp_formula, a).evalf(subs=dic) * er1.absolute_error()) ** 2
            s += (diff(symp_formula, b).evalf(subs=dic) * er2.absolute_error()) ** 2
            s += (diff(symp_formula, c).evalf(subs=dic) * er3.absolute_error()) ** 2
            s += (diff(symp_formula, d).evalf(subs=dic) * er4.absolute_error()) ** 2
            s += (diff(symp_formula, e).evalf(subs=dic) * er5.absolute_error()) ** 2
            s += (diff(symp_formula, f).evalf(subs=dic) * er6.absolute_error()) ** 2
            s += (diff(symp_formula, g).evalf(subs=dic) * er7.absolute_error()) ** 2
            s += (diff(symp_formula, h).evalf(subs=dic) * er8.absolute_error()) ** 2
            s += (diff(symp_formula, i).evalf(subs=dic) * er9.absolute_error()) ** 2
            s += (diff(symp_formula, j).evalf(subs=dic) * er10.absolute_error()) ** 2
            ind_absol_err = sqrt(s)
            ind_relative_err = (ind_absol_err / z_average) * 100
            if err == 'rel':
                return ind_relative_err
            else:
                return ind_absol_err

        def mfp():
            s = 0
            symp_formula2 = sympify("ln(" + self.formula + ")")
            s += (diff(symp_formula2, a).evalf(subs=dic) * er1.absolute_error()) ** 2
            s += (diff(symp_formula2, b).evalf(subs=dic) * er2.absolute_error()) ** 2
            s += (diff(symp_formula2, c).evalf(subs=dic) * er3.absolute_error()) ** 2
            s += (diff(symp_formula2, d).evalf(subs=dic) * er4.absolute_error()) ** 2
            s += (diff(symp_formula2, e).evalf(subs=dic) * er5.absolute_error()) ** 2
            s += (diff(symp_formula2, f).evalf(subs=dic) * er6.absolute_error()) ** 2
            s += (diff(symp_formula2, g).evalf(subs=dic) * er7.absolute_error()) ** 2
            s += (diff(symp_formula2, h).evalf(subs=dic) * er8.absolute_error()) ** 2
            s += (diff(symp_formula2, i).evalf(subs=dic) * er9.absolute_error()) ** 2
            s += (diff(symp_formula2, j).evalf(subs=dic) * er10.absolute_error()) ** 2
            ind_relative_err = sqrt(s) * 100
            ind_absol_err = z_average * ind_relative_err / 100
            if err == 'rel':
                return ind_relative_err
            else:
                return ind_absol_err

        if meth == "0":
            return mfs()
        else:
            return mfp()


# m = [[1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#      [2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [0], [0], [0], [0], [0], [0], [0], [0]]
# ins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# eoim = EOIM(m, ins, "(a)+(b)")
# print(eoim.mth("0"))
