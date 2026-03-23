from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Tuple

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from Error import Error


@dataclass
class IndirectMethodResult:
    method: str
    indirect_value: float
    absolute_error: float
    relative_error: float
    direct_means: Dict[str, float]
    direct_errors: Dict[str, float]
    result_string: str
    indirect_measurements: List[float] | None = None
    statistical_std: float | None = None


class IndirectMeasurementCalculator:
    def __init__(self, formula: str):
        if not formula.strip():
            raise ValueError("Формула не должна быть пустой.")
        self.formula = formula.strip()

    def method_statistical(self, direct_measurements: Dict[str, Error]) -> Dict:
        means = {var: error_obj.average_x() for var, error_obj in direct_measurements.items()}
        statistical_errors = {var: error_obj.confidence_interval() for var, error_obj in direct_measurements.items()}
        indirect_value, absolute_error, relative_error = self.calculate_single_error(means, statistical_errors)
        return IndirectMethodResult(
            method="Статистические погрешности",
            indirect_value=indirect_value,
            absolute_error=absolute_error,
            relative_error=relative_error,
            direct_means=means,
            direct_errors=statistical_errors,
            result_string=f"{indirect_value:.6f} ± {absolute_error:.6f} (стат.)",
        ).__dict__

    def method_instrumental(self, direct_measurements: Dict[str, Error]) -> Dict:
        means = {var: error_obj.average_x() for var, error_obj in direct_measurements.items()}
        instrumental_errors = {var: error_obj.instrumental_component() for var, error_obj in direct_measurements.items()}
        indirect_value, absolute_error, relative_error = self.calculate_single_error(means, instrumental_errors)
        return IndirectMethodResult(
            method="Инструментальные погрешности",
            indirect_value=indirect_value,
            absolute_error=absolute_error,
            relative_error=relative_error,
            direct_means=means,
            direct_errors=instrumental_errors,
            result_string=f"{indirect_value:.6f} ± {absolute_error:.6f} (приб.)",
        ).__dict__

    def method_combined(self, direct_measurements: Dict[str, Error]) -> Dict:
        means = {var: error_obj.average_x() for var, error_obj in direct_measurements.items()}
        combined_errors = {var: error_obj.absolute_error() for var, error_obj in direct_measurements.items()}
        indirect_value, absolute_error, relative_error = self.calculate_single_error(means, combined_errors)
        return IndirectMethodResult(
            method="Комбинированные погрешности",
            indirect_value=indirect_value,
            absolute_error=absolute_error,
            relative_error=relative_error,
            direct_means=means,
            direct_errors=combined_errors,
            result_string=f"{indirect_value:.6f} ± {absolute_error:.6f} (полн.)",
        ).__dict__

    def method_individual(self, direct_measurements: Dict[str, Error]) -> Dict:
        measurement_counts = [len(error_obj.arr) for error_obj in direct_measurements.values()]
        if len(set(measurement_counts)) != 1:
            raise ValueError("Для индивидуального метода у всех переменных должно быть одинаковое количество измерений.")

        indirect_measurements = []
        for index in range(measurement_counts[0]):
            measurement_dict = {var: error_obj.arr[index] for var, error_obj in direct_measurements.items()}
            indirect_measurements.append(self.calculate_indirect_value(measurement_dict))

        means = {var: error_obj.average_x() for var, error_obj in direct_measurements.items()}
        instrumental_errors = {var: error_obj.instrumental_component() for var, error_obj in direct_measurements.items()}
        indirect_instrumental_error = self.calculate_absolute_error(means, instrumental_errors)
        indirect_error_obj = Error(indirect_measurements, indirect_instrumental_error)

        return IndirectMethodResult(
            method="Индивидуальные измерения",
            indirect_value=indirect_error_obj.average_x(),
            absolute_error=indirect_error_obj.absolute_error(),
            relative_error=indirect_error_obj.relative_error(),
            direct_means=means,
            direct_errors=instrumental_errors,
            indirect_measurements=indirect_measurements,
            statistical_std=indirect_error_obj.dispersion_x(),
            result_string=f"{indirect_error_obj.average_x():.6f} ± {indirect_error_obj.absolute_error():.6f} (индив.)",
        ).__dict__

    def calculate_single_error(self, means: Dict[str, float], errors: Dict[str, float]) -> Tuple[float, float, float]:
        indirect_value = self.calculate_indirect_value(means)
        absolute_error = self.calculate_absolute_error(means, errors)
        relative_error = (absolute_error / abs(indirect_value)) * 100 if indirect_value != 0 else float("inf")
        return indirect_value, absolute_error, relative_error

    def calculate_indirect_value(self, values_dict: Dict[str, float]) -> float:
        expr = self._parse_expression(values_dict.keys())
        return float(expr.subs(values_dict))

    def calculate_absolute_error(self, means: Dict[str, float], errors: Dict[str, float]) -> float:
        expr, var_dict = self._parse_expression_with_symbols(means.keys())
        error_squared_sum = 0.0

        for var_name, symbol in var_dict.items():
            derivative = sp.diff(expr, symbol)
            partial_value = float(derivative.subs(means))
            error_squared_sum += (partial_value * errors[var_name]) ** 2

        return math.sqrt(error_squared_sum)

    def compare_all_methods(self, direct_measurements: Dict[str, Error]) -> Dict[str, Dict]:
        return {
            "method1": self.method_statistical(direct_measurements),
            "method2": self.method_instrumental(direct_measurements),
            "method3": self.method_combined(direct_measurements),
            "method4": self.method_individual(direct_measurements),
        }

    def _parse_expression(self, variable_names) -> sp.Expr:
        expr, _ = self._parse_expression_with_symbols(variable_names)
        return expr

    def _parse_expression_with_symbols(self, variable_names) -> Tuple[sp.Expr, Dict[str, sp.Symbol]]:
        ordered_names = list(variable_names)
        symbols = sp.symbols(" ".join(ordered_names))
        if not isinstance(symbols, tuple):
            symbols = (symbols,)

        local_dict = dict(zip(ordered_names, symbols))
        expr = parse_expr(self.formula, local_dict=local_dict)
        return expr, local_dict
