import EOIM
import Data
dat = Data.Data(2)
ins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
eoim = EOIM.EOIM(dat.data(), ins, "(a)+(b)")
print(eoim.mth("1"))