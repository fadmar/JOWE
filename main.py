from EOIM import EOIM
from Error import Error
import Data
import Inst
# example
#dat = Data.Data(2)
#ins = Inst.Inst()
#from Error import Error
#err = Error([0, 1, 1], 0)
#print(err.absolute_error())
from EOIM import EOIM
eoim = EOIM(dat.data(), ins.inst(), "a+b**2")
print(eoim.mth("0","rel"))
