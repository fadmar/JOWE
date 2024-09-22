
class Data:
    def __init__(self, number_of_measurements):
        self.number_of_measurements = number_of_measurements  # количество измерений

    def data(self):
        allmsm = [0] * self.number_of_measurements
        for i in range(self.number_of_measurements):
            with open('Data/data' + str(i + 1) + '.txt', 'r') as f:
                x = f.read().splitlines()
                for j in range(len(x)):
                    x[j] = float(x[j])
            allmsm[i] = x
        return allmsm
