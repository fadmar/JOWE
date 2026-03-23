from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, List


@dataclass
class Error:
    arr: List[float]
    inst_err: float

    def __init__(self, arr: Iterable[float], inst_err: float):
        values = [float(value) for value in arr]
        if not values:
            raise ValueError("Список измерений не должен быть пустым.")

        self.arr = values
        self.inst_err = float(inst_err)

    def average_x(self) -> float:
        return sum(self.arr) / len(self.arr)

    def dispersion_x(self) -> float:
        if len(self.arr) < 2:
            return 0.0

        average = self.average_x()
        squared_diffs = [(value - average) ** 2 for value in self.arr]
        return math.sqrt(sum(squared_diffs) / (len(self.arr) - 1))

    def confidence_interval(self) -> float:
        if len(self.arr) < 2:
            return 0.0

        coefficients = [0.0, 12.7, 4.30, 3.18, 2.78, 2.57, 2.45, 2.36, 2.31, 2.26, 2.09, 2.04, 2.0]
        sample_size = len(self.arr)

        if sample_size <= 10:
            coefficient = coefficients[sample_size - 1]
        elif sample_size < 30:
            coefficient = coefficients[10]
        elif sample_size < 60:
            coefficient = coefficients[11]
        else:
            coefficient = coefficients[12]

        return coefficient * self.dispersion_x()

    def instrumental_component(self) -> float:
        return (2.0 / 3.0) * self.inst_err

    def absolute_error(self) -> float:
        return math.sqrt(self.confidence_interval() ** 2 + self.instrumental_component() ** 2)

    def relative_error(self) -> float:
        average = self.average_x()
        if average == 0:
            return float("inf")
        return (self.absolute_error() / abs(average)) * 100

    def summary(self) -> dict:
        return {
            "count": len(self.arr),
            "mean": self.average_x(),
            "std": self.dispersion_x(),
            "confidence_interval": self.confidence_interval(),
            "instrumental_error": self.inst_err,
            "absolute_error": self.absolute_error(),
            "relative_error": self.relative_error(),
        }
