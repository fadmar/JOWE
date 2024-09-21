import math
class Error:
    def __init__(self, arr, inst_err):
        self.arr = arr
        self.inst_err = inst_err

    def average_x(self):
        return sum(self.arr) / len(self.arr)

    def dispersion_x(self):
        n = len(self.arr)
        m = [0] * n
        for i in range(n):
            x = self.arr[i]
            m[i] = (x - Error.average_x(self)) ** 2
        dis = math.sqrt(sum(m) / n * (n - 1))
        return dis

    def confidence_interval(self):
        Ks = [0, 12.7, 4.30, 3.18, 2.78, 2.57, 2.45, 2.36, 2.31, 2.26, 2.09, 2.04, 2.0]
        if len(self.arr) < 11:
            return Ks[len(self.arr) - 1] * Error.dispersion_x(self)
        elif len(self.arr) < 30:
            return Ks[10] * Error.dispersion_x(self)
        elif len(self.arr) < 60:
            return Ks[11] * Error.dispersion_x(self)
        else:
            return Ks[12] * Error.dispersion_x(self)

    def absolute_error(self):
        return math.sqrt(Error.confidence_interval(self) ** 2 + ((2 / 3) * self.inst_err) ** 2)

    def relative_error(self):
        return (Error.absolute_error(self) / Error.average_x(self)) * 100