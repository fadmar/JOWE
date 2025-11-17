from Error import Error
from IndirectMeasurementCalculator import IndirectMeasurementCalculator
#пример использования
if __name__ == "__main__":
    #пример 1: Закон Ома R = U / I

    #прямые измерения напряжения
    U_measurements = [12.1, 12.2, 12.0, 12.3, 12.1, 12.2, 12.0, 12.1, 12.2, 12.1]
    U_inst_error = 0.05
    U_error = Error(U_measurements, U_inst_error)

    #прямые измерения тока
    I_measurements = [0.251, 0.249, 0.252, 0.248, 0.250, 0.251, 0.249, 0.250, 0.252, 0.249]
    I_inst_error = 0.002
    I_error = Error(I_measurements, I_inst_error)

    direct_measurements = {'U': U_error, 'I': I_error}

    #создаем объект для расчета косвенной погрешности
    calculator = IndirectMeasurementCalculator("U / I")

    #сравниваем все методы
    results = calculator.compare_all_methods(direct_measurements)

    #информация о прямых измерениях
    print(f"\nИНФОРМАЦИЯ О ПРЯМЫХ ИЗМЕРЕНИЯХ ")
    for var, error_obj in direct_measurements.items():
        print(f"{var}: {error_obj.average_x():.4f} ± {error_obj.absolute_error():.4f} "
              f"(отн. {error_obj.relative_error():.2f}%)")

    print("\n\n")

    #пример 2: площадь прямоугольника S = a * b

    a_measurements = [5.1, 5.0, 5.2, 5.1, 5.0]
    a_inst_error = 0.1
    a_error = Error(a_measurements, a_inst_error)

    b_measurements = [3.2, 3.1, 3.3, 3.2, 3.1]
    b_inst_error = 0.1
    b_error = Error(b_measurements, b_inst_error)

    direct_measurements_rect = {'a': a_error, 'b': b_error}

    calculator_rect = IndirectMeasurementCalculator("a * b")
    results_rect = calculator_rect.compare_all_methods(direct_measurements_rect)