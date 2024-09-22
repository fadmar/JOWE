class Inst:
    def inst(self):
        with open('Data/inst.txt', 'r') as f:
            x = f.read().splitlines()
            x = x + [0] * 10
            for j in range(len(x)):
                x[j] = float(x[j])
        return x