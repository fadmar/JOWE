from __future__ import annotations

from io import BytesIO
from typing import Dict, Iterable

from matplotlib.figure import Figure

from Error import Error


def histogram_figure(variable_name: str, error_obj: Error, unit: str = "") -> Figure:
    figure = Figure(figsize=(8, 4.5), dpi=120)
    axis = figure.add_subplot(111)
    bins = min(12, max(5, len(error_obj.arr) // 2 or 1))
    axis.hist(error_obj.arr, bins=bins, color="#5B8DEF", edgecolor="white")

    mean = error_obj.average_x()
    absolute_error = error_obj.absolute_error()
    axis.axvline(mean, color="#C0392B", linewidth=2, label=f"Среднее: {mean:.4g}")
    axis.axvline(mean - absolute_error, color="#E67E22", linestyle="--", linewidth=1.7, label="Среднее ± погрешность")
    axis.axvline(mean + absolute_error, color="#E67E22", linestyle="--", linewidth=1.7)
    axis.set_title(f"Гистограмма измерений: {variable_name}")
    axis.set_xlabel(f"Значение{f', {unit}' if unit else ''}")
    axis.set_ylabel("Частота")
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    return figure


def direct_error_comparison_figure(variables: Iterable[dict], direct_measurements: Dict[str, Error]) -> Figure:
    variables = list(variables)
    names = [item["name"] for item in variables]
    means = [direct_measurements[name].average_x() for name in names]
    errors = [direct_measurements[name].absolute_error() for name in names]

    figure = Figure(figsize=(8, 4.5), dpi=120)
    axis = figure.add_subplot(111)
    axis.bar(names, means, yerr=errors, capsize=8, color="#2C7A7B", alpha=0.9)
    axis.set_title("Сравнение прямых измерений")
    axis.set_ylabel("Среднее значение")
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    return figure


def indirect_methods_figure(indirect_results: Dict[str, Dict]) -> Figure:
    results = list(indirect_results.values())
    labels = [result["method"] for result in results]
    values = [result["indirect_value"] for result in results]
    errors = [result["absolute_error"] for result in results]

    figure = Figure(figsize=(8, 4.5), dpi=120)
    axis = figure.add_subplot(111)
    axis.barh(labels, values, xerr=errors, color="#E67E22", alpha=0.9)
    axis.set_title("Сравнение методов косвенной погрешности")
    axis.set_xlabel("Значение")
    axis.grid(axis="x", alpha=0.25)
    figure.tight_layout()
    return figure


def individual_measurements_figure(indirect_results: Dict[str, Dict]) -> Figure:
    individual = indirect_results["method4"].get("indirect_measurements") or []
    if not individual:
        raise ValueError("Нет данных для графика индивидуальных измерений.")

    figure = Figure(figsize=(8, 4.5), dpi=120)
    axis = figure.add_subplot(111)
    axis.plot(range(1, len(individual) + 1), individual, marker="o", color="#8E44AD", linewidth=1.8)
    axis.set_title("Индивидуальные значения косвенной величины")
    axis.set_xlabel("Номер измерения")
    axis.set_ylabel("Значение")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    return figure


def figure_to_png_bytes(figure: Figure) -> bytes:
    stream = BytesIO()
    figure.savefig(stream, format="png", dpi=160, bbox_inches="tight")
    return stream.getvalue()
