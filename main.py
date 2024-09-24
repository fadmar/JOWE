# example1
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from Data import Data
from Inst import Inst
from UseFunc import UseFunc
dat = Data(1)
#inst = Inst()
# example2
#from Error import Error
#err = Error([0, 1, 1], 0)
#print(err.absolute_error())
# example3
# from EOIM import EOIM
# eoim = EOIM(dat.data(), inst.inst(), "a+b**2")
# print(eoim.mth("0","rel"))
usef = UseFunc(dat.data()[0])
usef.gaussian_function(3)



x = sp.symbols('x')
y = usef.gaussian_function(x)
plt.style.use('bmh')
sp.plot(y)
