import Error
import Data
import math
dat = Data.Data(1)
er = Error.Error(dat.data()[0], 0.1)
print(dat.data())
print(er.average_x())
print(er.dispersion_x())
print(er.absolute_error())
print(er.relative_error())
