import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from typing import List, Dict, Union, Tuple
from Error import Error
import math

class IndirectMeasurementCalculator:

    #расчет погрешностей косвенных измерений

    def __init__(self, formula: str):
        #класс при инициализации должен получить формулу по которой считается косвенная величина
        self.formula = formula

    def method_statistical(self, direct_measurements: Dict[str, Error]) -> Dict:

        #МЕТОД 1: использует только статистические погрешности, можно использовать когда инструментальные пренебрежимо малы

        #получаем средние значения и статистические погрешности
        means = {}
        statistical_errors = {}

        for var, error_obj in direct_measurements.items():
            means[var] = error_obj.average_x()
            #используем только статистическую составляющую (доверительный интервал)
            statistical_errors[var] = error_obj.confidence_interval()

        #вычисляем косвенную величину и ее погрешность
        indirect_value, absolute_error, relative_error = self.calculate_single_error(
            means, statistical_errors
        )

        return {
            'method': 'Статистические погрешности',
            'indirect_value': indirect_value,
            'absolute_error': absolute_error,
            'relative_error': relative_error,
            'direct_means': means,
            'direct_errors': statistical_errors,
            'result_string': f"{indirect_value:.6f} ± {absolute_error:.6f} (стат.)"
        }

    def method_instrumental(self, direct_measurements: Dict[str, Error]) -> Dict:

        #МЕТОД 2: использует только инструментальные погрешности, можно использовать когда статистические очень малы

        #получаем средние значения и инструментальные погрешности
        means = {}
        instrumental_errors = {}

        for var, error_obj in direct_measurements.items():
            means[var] = error_obj.average_x()
            #используем только инструментальную составляющую
            instrumental_errors[var] = (2 / 3) * error_obj.inst_err

        #вычисляем косвенную величину и ее погрешность
        indirect_value, absolute_error, relative_error = self.calculate_single_error(
            means, instrumental_errors
        )

        return {
            'method': 'Инструментальные погрешности',
            'indirect_value': indirect_value,
            'absolute_error': absolute_error,
            'relative_error': relative_error,
            'direct_means': means,
            'direct_errors': instrumental_errors,
            'result_string': f"{indirect_value:.6f} ± {absolute_error:.6f} (приб.)"
        }

    def method_combined(self, direct_measurements: Dict[str, Error]) -> Dict:

        #МЕТОД 3: использует комбинированные погрешности (статистические + инструментальные)

        #получаем средние значения и полные погрешности из класса Error
        means = {}
        combined_errors = {}

        for var, error_obj in direct_measurements.items():
            means[var] = error_obj.average_x()
            combined_errors[var] = error_obj.absolute_error()

        #вычисляем косвенную величину и ее погрешность
        indirect_value, absolute_error, relative_error = self.calculate_single_error(
            means, combined_errors
        )

        return {
            'method': 'Комбинированные погрешности',
            'indirect_value': indirect_value,
            'absolute_error': absolute_error,
            'relative_error': relative_error,
            'direct_means': means,
            'direct_errors': combined_errors,
            'result_string': f"{indirect_value:.6f} ± {absolute_error:.6f} (полн.)"
        }

    def method_individual(self, direct_measurements: Dict[str, Error]) -> Dict:
        #МЕТОД 4: Анализ индивидуальных измерений
        """
        Вычисляет косвенную величину для каждого набора прямых измерений,
        затем создает объект Error для массива косвенных измерений
        """

        #проверяем, что все массивы измерений имеют одинаковую длину
        measurement_counts = [len(error_obj.arr) for error_obj in direct_measurements.values()]
        if len(set(measurement_counts)) != 1:
            raise ValueError("Все прямые измерения должны иметь одинаковое количество данных")

        n_measurements = measurement_counts[0]
        variables = list(direct_measurements.keys())

        #вычисляем косвенную величину для каждого набора измерений
        indirect_measurements = []

        for i in range(n_measurements):
            #собираем i-е измерение для всех величин
            measurement_dict = {}
            for var, error_obj in direct_measurements.items():
                measurement_dict[var] = error_obj.arr[i]

            #вычисляем косвенную величину для этого набора
            indirect_value = self.calculate_indirect_value(measurement_dict)
            indirect_measurements.append(indirect_value)

        #вычисляем инструментальную погрешность для косвенной величины
        means = {var: error_obj.average_x() for var, error_obj in direct_measurements.items()}
        instrumental_errors = {var: (2 / 3) * error_obj.inst_err for var, error_obj in direct_measurements.items()}

        indirect_instrumental_error = self.calculate_absolute_error(means, instrumental_errors)

        #создаем объект Error для массива косвенных измерений
        indirect_error_obj = Error(indirect_measurements, indirect_instrumental_error)

        return {
            'method': 'Индивидуальные измерения',
            'indirect_measurements': indirect_measurements,
            'indirect_value': indirect_error_obj.average_x(),
            'absolute_error': indirect_error_obj.absolute_error(),
            'relative_error': indirect_error_obj.relative_error(),
            'statistical_std': indirect_error_obj.dispersion_x(),
            'result_string': f"{indirect_error_obj.average_x():.6f} ± {indirect_error_obj.absolute_error():.6f} (индив.)"
        }

    def calculate_single_error(self, means: Dict[str, float], errors: Dict[str, float]) -> Tuple[float, float, float]:
        #вычисляем косвенную величину и ее погрешность для одного набора значений
        indirect_value = self.calculate_indirect_value(means)
        absolute_error = self.calculate_absolute_error(means, errors)
        relative_error = (absolute_error / abs(indirect_value)) * 100 if indirect_value != 0 else float('inf')

        return indirect_value, absolute_error, relative_error

    def calculate_indirect_value(self, values_dict: Dict[str, float]) -> float:
        #вычисляем значение косвенной величины по формуле
        variables = list(values_dict.keys())
        sym_vars = sp.symbols(' '.join(variables))
        var_dict = dict(zip(variables, sym_vars))

        expr = parse_expr(self.formula, var_dict)
        values = {var: values_dict[var] for var in variables}

        return float(expr.subs(values))

    def calculate_absolute_error(self, means: Dict[str, float], errors: Dict[str, float]) -> float:
        #вычисляем абсолютную погрешность косвенной величины
        variables = list(means.keys())
        sym_vars = sp.symbols(' '.join(variables))
        var_dict = dict(zip(variables, sym_vars))

        expr = parse_expr(self.formula, var_dict)

        #вычисляем частные производные
        partial_derivatives = {}
        for var in variables:
            partial_derivatives[var] = sp.diff(expr, var_dict[var])

        #вычисляем абсолютную погрешность по формуле переноса
        error_squared_sum = 0
        for var in variables:
            partial_value = float(partial_derivatives[var].subs(means))
            error_contribution = (partial_value * errors[var]) ** 2
            error_squared_sum += error_contribution

        return math.sqrt(error_squared_sum)

    def compare_all_methods(self, direct_measurements: Dict[str, Error]) -> Dict:
        #сравнивает все 4 метода и возвращает результаты
        results = {}

        results['method1'] = self.method_statistical(direct_measurements)
        results['method2'] = self.method_instrumental(direct_measurements)
        results['method3'] = self.method_combined(direct_measurements)
        results['method4'] = self.method_individual(direct_measurements)

        print("СРАВНЕНИЕ МЕТОДОВ")
        print(f"Формула: {self.formula}")

        for key, result in results.items():
            print(f"{result['method']}: {result['result_string']} "
                  f"(отн. погр.: {result['relative_error']:.2f}%)")

        return results
