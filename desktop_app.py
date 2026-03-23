from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Error import Error
from IndirectMeasurementCalculator import IndirectMeasurementCalculator
from excel_io import create_template, export_report, import_measurements
from plotting import (
    direct_error_comparison_figure,
    figure_to_png_bytes,
    histogram_figure,
    indirect_methods_figure,
    individual_measurements_figure,
)


class MeasurementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JOWE - Расчет погрешностей измерений")
        self.geometry("1400x860")
        self.minsize(1180, 760)

        self.formula_var = tk.StringVar(value="U / I")
        self.result_name_var = tk.StringVar(value="R")
        self.selected_variable_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Готово к работе.")

        self.variables: list[dict] = []
        self.direct_measurements: dict[str, Error] = {}
        self.indirect_results: dict[str, dict] = {}
        self.graph_cache: dict[str, bytes] = {}
        self.current_figure = None
        self.current_canvas = None

        self._build_layout()
        self._load_demo_data()

    def _build_layout(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        controls = ttk.Frame(self, padding=14)
        controls.grid(row=0, column=0, sticky="nsw")
        controls.columnconfigure(0, weight=1)

        content = ttk.Frame(self, padding=(0, 14, 14, 14))
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(2, weight=1)

        ttk.Label(controls, text="Формула косвенного измерения").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.formula_var, width=32).grid(row=1, column=0, sticky="ew", pady=(4, 10))
        ttk.Label(controls, text="Имя результата").grid(row=2, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.result_name_var, width=32).grid(row=3, column=0, sticky="ew", pady=(4, 12))

        ttk.Label(controls, text="Переменные и измерения").grid(row=4, column=0, sticky="w")
        self.variables_tree = ttk.Treeview(
            controls,
            columns=("instrumental", "unit", "count", "preview"),
            show="tree headings",
            height=12,
        )
        self.variables_tree.heading("#0", text="Переменная")
        self.variables_tree.heading("instrumental", text="Приб. погр.")
        self.variables_tree.heading("unit", text="Ед.")
        self.variables_tree.heading("count", text="N")
        self.variables_tree.heading("preview", text="Измерения")
        self.variables_tree.column("#0", width=110, anchor="w")
        self.variables_tree.column("instrumental", width=95, anchor="center")
        self.variables_tree.column("unit", width=60, anchor="center")
        self.variables_tree.column("count", width=50, anchor="center")
        self.variables_tree.column("preview", width=260)
        self.variables_tree.grid(row=5, column=0, sticky="nsew")

        variables_buttons = ttk.Frame(controls)
        variables_buttons.grid(row=6, column=0, sticky="ew", pady=(8, 16))
        for column_index in range(3):
            variables_buttons.columnconfigure(column_index, weight=1)
        ttk.Button(variables_buttons, text="Добавить", command=self.add_variable).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(variables_buttons, text="Изменить", command=self.edit_variable).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(variables_buttons, text="Удалить", command=self.delete_variable).grid(row=0, column=2, sticky="ew", padx=(4, 0))

        file_buttons = ttk.LabelFrame(controls, text="Excel")
        file_buttons.grid(row=7, column=0, sticky="ew")
        file_buttons.columnconfigure(0, weight=1)
        ttk.Button(file_buttons, text="Импорт из Excel", command=self.import_from_excel).grid(row=0, column=0, sticky="ew", pady=(6, 4), padx=8)
        ttk.Button(file_buttons, text="Экспорт отчета в Excel", command=self.export_to_excel).grid(row=1, column=0, sticky="ew", pady=4, padx=8)
        ttk.Button(file_buttons, text="Сохранить шаблон Excel", command=self.save_excel_template).grid(row=2, column=0, sticky="ew", pady=(4, 8), padx=8)

        compute_box = ttk.Frame(controls)
        compute_box.grid(row=8, column=0, sticky="ew", pady=(16, 0))
        compute_box.columnconfigure(0, weight=1)
        ttk.Button(compute_box, text="Рассчитать", command=self.calculate_results).grid(row=0, column=0, sticky="ew")

        ttk.Label(content, text="Результаты расчетов", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.results_tree = ttk.Treeview(content, columns=("value", "abs_error", "rel_error", "details"), show="tree headings", height=8)
        self.results_tree.heading("#0", text="Метод")
        self.results_tree.heading("value", text="Значение")
        self.results_tree.heading("abs_error", text="Абс. погр.")
        self.results_tree.heading("rel_error", text="Отн. погр., %")
        self.results_tree.heading("details", text="Описание")
        self.results_tree.column("#0", width=210, anchor="w")
        self.results_tree.column("value", width=120, anchor="center")
        self.results_tree.column("abs_error", width=120, anchor="center")
        self.results_tree.column("rel_error", width=120, anchor="center")
        self.results_tree.column("details", width=430)
        self.results_tree.grid(row=1, column=0, sticky="ew", pady=(8, 12))

        graph_controls = ttk.LabelFrame(content, text="Графики")
        graph_controls.grid(row=2, column=0, sticky="nsew")
        graph_controls.columnconfigure(1, weight=1)
        graph_controls.rowconfigure(1, weight=1)

        top_controls = ttk.Frame(graph_controls)
        top_controls.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        ttk.Label(top_controls, text="Переменная для гистограммы:").grid(row=0, column=0, sticky="w")
        self.variable_combo = ttk.Combobox(top_controls, textvariable=self.selected_variable_var, state="readonly", width=14)
        self.variable_combo.grid(row=0, column=1, sticky="w", padx=(8, 16))
        ttk.Button(top_controls, text="Гистограмма", command=lambda: self.render_graph("histogram")).grid(row=0, column=2, padx=4)
        ttk.Button(top_controls, text="Прямые погрешности", command=lambda: self.render_graph("direct")).grid(row=0, column=3, padx=4)
        ttk.Button(top_controls, text="Методы косвенной", command=lambda: self.render_graph("indirect")).grid(row=0, column=4, padx=4)
        ttk.Button(top_controls, text="Индивидуальные", command=lambda: self.render_graph("individual")).grid(row=0, column=5, padx=4)
        ttk.Button(top_controls, text="Экспорт графика PNG", command=self.export_current_graph).grid(row=0, column=6, padx=(16, 4))

        self.graph_frame = ttk.Frame(graph_controls)
        self.graph_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 8))
        self.graph_frame.columnconfigure(0, weight=1)
        self.graph_frame.rowconfigure(0, weight=1)

        status = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w", padding=(8, 4))
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _load_demo_data(self) -> None:
        self.variables = [
            {"name": "U", "instrumental_error": 0.05, "unit": "V", "measurements": [12.1, 12.2, 12.0, 12.3, 12.1, 12.2, 12.0, 12.1]},
            {"name": "I", "instrumental_error": 0.002, "unit": "A", "measurements": [0.251, 0.249, 0.252, 0.248, 0.250, 0.251, 0.249, 0.250]},
        ]
        self._refresh_variables_view()
        self.calculate_results()

    def add_variable(self) -> None:
        variable = self._prompt_variable()
        if not variable:
            return
        if any(item["name"] == variable["name"] for item in self.variables):
            messagebox.showerror("Ошибка", "Переменная с таким именем уже существует.")
            return
        self.variables.append(variable)
        self._refresh_variables_view()
        self.status_var.set(f"Добавлена переменная {variable['name']}.")

    def edit_variable(self) -> None:
        selected = self.variables_tree.selection()
        if not selected:
            messagebox.showinfo("Изменение", "Сначала выберите переменную в таблице.")
            return
        name = selected[0]
        index = self._find_variable_index(name)
        updated = self._prompt_variable(self.variables[index])
        if not updated:
            return
        duplicate = any(item["name"] == updated["name"] and idx != index for idx, item in enumerate(self.variables))
        if duplicate:
            messagebox.showerror("Ошибка", "Переменная с таким именем уже существует.")
            return
        self.variables[index] = updated
        self._refresh_variables_view()
        self.status_var.set(f"Обновлена переменная {updated['name']}.")

    def delete_variable(self) -> None:
        selected = self.variables_tree.selection()
        if not selected:
            messagebox.showinfo("Удаление", "Сначала выберите переменную в таблице.")
            return
        name = selected[0]
        self.variables = [item for item in self.variables if item["name"] != name]
        self._refresh_variables_view()
        self.status_var.set(f"Удалена переменная {name}.")

    def _prompt_variable(self, initial: dict | None = None) -> dict | None:
        dialog = VariableDialog(self, initial)
        self.wait_window(dialog)
        return dialog.result

    def import_from_excel(self) -> None:
        path = filedialog.askopenfilename(title="Выберите Excel-файл", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not path:
            return

        try:
            data = import_measurements(path)
        except Exception as exc:
            messagebox.showerror("Ошибка импорта", str(exc))
            return

        self.formula_var.set(data["formula"])
        self.result_name_var.set(data["result_name"])
        self.variables = data["variables"]
        self._refresh_variables_view()
        self.calculate_results()
        self.status_var.set(f"Данные импортированы из {Path(path).name}.")

    def export_to_excel(self) -> None:
        if not self.indirect_results:
            self.calculate_results()
        self._prepare_all_graphs_for_export()
        path = filedialog.asksaveasfilename(title="Сохранить Excel-отчет", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return

        try:
            export_report(
                path=path,
                formula=self.formula_var.get().strip(),
                result_name=self.result_name_var.get().strip() or "Result",
                variables=self.variables,
                direct_measurements=self.direct_measurements,
                indirect_results=self.indirect_results,
                graph_images=self.graph_cache or None,
            )
        except Exception as exc:
            messagebox.showerror("Ошибка экспорта", str(exc))
            return

        self.status_var.set(f"Excel-отчет сохранен: {Path(path).name}")

    def save_excel_template(self) -> None:
        path = filedialog.asksaveasfilename(title="Сохранить шаблон Excel", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return

        try:
            create_template(path)
        except Exception as exc:
            messagebox.showerror("Ошибка", str(exc))
            return

        self.status_var.set(f"Шаблон сохранен: {Path(path).name}")

    def calculate_results(self) -> None:
        try:
            self._ensure_ready_for_calculation()
            self.direct_measurements = {
                variable["name"]: Error(variable["measurements"], variable["instrumental_error"])
                for variable in self.variables
            }
            calculator = IndirectMeasurementCalculator(self.formula_var.get().strip())
            self.indirect_results = calculator.compare_all_methods(self.direct_measurements)
        except Exception as exc:
            messagebox.showerror("Ошибка расчета", str(exc))
            return

        self.results_tree.delete(*self.results_tree.get_children())
        for key, result in self.indirect_results.items():
            self.results_tree.insert(
                "",
                "end",
                iid=key,
                text=result["method"],
                values=(
                    f"{result['indirect_value']:.6g}",
                    f"{result['absolute_error']:.6g}",
                    f"{result['relative_error']:.4g}",
                    result["result_string"],
                ),
            )

        self.render_graph("histogram", silent=True)
        self.status_var.set("Расчеты обновлены.")

    def render_graph(self, graph_type: str, silent: bool = False) -> None:
        if not self.direct_measurements or not self.indirect_results:
            if not silent:
                messagebox.showinfo("Графики", "Сначала выполните расчет.")
            return

        try:
            if graph_type == "histogram":
                variable_name = self.selected_variable_var.get() or self.variables[0]["name"]
                self.selected_variable_var.set(variable_name)
                variable = next(item for item in self.variables if item["name"] == variable_name)
                figure = histogram_figure(variable_name, self.direct_measurements[variable_name], variable.get("unit", ""))
                cache_key = f"Гистограмма {variable_name}"
            elif graph_type == "direct":
                figure = direct_error_comparison_figure(self.variables, self.direct_measurements)
                cache_key = "Сравнение прямых погрешностей"
            elif graph_type == "indirect":
                figure = indirect_methods_figure(self.indirect_results)
                cache_key = "Сравнение методов косвенной погрешности"
            elif graph_type == "individual":
                figure = individual_measurements_figure(self.indirect_results)
                cache_key = "Индивидуальные значения косвенной величины"
            else:
                raise ValueError("Неизвестный тип графика.")
        except Exception as exc:
            if not silent:
                messagebox.showerror("Ошибка графика", str(exc))
            return

        self._show_figure(figure)
        self.graph_cache[cache_key] = figure_to_png_bytes(figure)
        self.status_var.set(f"Построен график: {cache_key}")

    def export_current_graph(self) -> None:
        if self.current_figure is None:
            messagebox.showinfo("Экспорт графика", "Сначала постройте график.")
            return
        path = filedialog.asksaveasfilename(title="Сохранить график", defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if not path:
            return
        self.current_figure.savefig(path, format="png", dpi=180, bbox_inches="tight")
        self.status_var.set(f"График сохранен: {Path(path).name}")

    def _prepare_all_graphs_for_export(self) -> None:
        if not self.variables or not self.direct_measurements or not self.indirect_results:
            return

        first_variable = self.variables[0]
        figures = {
            f"Гистограмма {first_variable['name']}": histogram_figure(
                first_variable["name"],
                self.direct_measurements[first_variable["name"]],
                first_variable.get("unit", ""),
            ),
            "Сравнение прямых погрешностей": direct_error_comparison_figure(self.variables, self.direct_measurements),
            "Сравнение методов косвенной погрешности": indirect_methods_figure(self.indirect_results),
        }

        try:
            figures["Индивидуальные значения косвенной величины"] = individual_measurements_figure(self.indirect_results)
        except Exception:
            pass

        for title, figure in figures.items():
            self.graph_cache[title] = figure_to_png_bytes(figure)

    def _show_figure(self, figure) -> None:
        if self.current_canvas is not None:
            self.current_canvas.get_tk_widget().destroy()
        self.current_figure = figure
        self.current_canvas = FigureCanvasTkAgg(figure, master=self.graph_frame)
        self.current_canvas.draw()
        self.current_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _refresh_variables_view(self) -> None:
        self.variables_tree.delete(*self.variables_tree.get_children())
        names = []
        for variable in self.variables:
            names.append(variable["name"])
            preview = ", ".join(format(value, ".6g") for value in variable["measurements"][:5])
            if len(variable["measurements"]) > 5:
                preview += ", ..."
            self.variables_tree.insert(
                "",
                "end",
                iid=variable["name"],
                text=variable["name"],
                values=(
                    format(variable["instrumental_error"], ".6g"),
                    variable.get("unit", ""),
                    len(variable["measurements"]),
                    preview,
                ),
            )

        self.variable_combo["values"] = names
        if names and self.selected_variable_var.get() not in names:
            self.selected_variable_var.set(names[0])
        elif not names:
            self.selected_variable_var.set("")

    def _find_variable_index(self, name: str) -> int:
        for index, variable in enumerate(self.variables):
            if variable["name"] == name:
                return index
        raise ValueError(f"Переменная {name} не найдена.")

    def _ensure_ready_for_calculation(self) -> None:
        if not self.formula_var.get().strip():
            raise ValueError("Введите формулу косвенного измерения.")
        if not self.variables:
            raise ValueError("Добавьте хотя бы одну переменную.")


class VariableDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, initial: dict | None = None):
        super().__init__(parent)
        self.result = None
        self.title("Переменная")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.name_var = tk.StringVar(value=(initial or {}).get("name", ""))
        self.instrumental_var = tk.StringVar(value=str((initial or {}).get("instrumental_error", 0.0)))
        self.unit_var = tk.StringVar(value=(initial or {}).get("unit", ""))
        initial_measurements = (initial or {}).get("measurements", [])
        self.measurements_text = tk.Text(self, width=52, height=8)

        ttk.Label(self, text="Имя переменной").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        ttk.Entry(self, textvariable=self.name_var, width=30).grid(row=1, column=0, sticky="ew", padx=12)
        ttk.Label(self, text="Инструментальная погрешность").grid(row=2, column=0, sticky="w", padx=12, pady=(10, 4))
        ttk.Entry(self, textvariable=self.instrumental_var, width=30).grid(row=3, column=0, sticky="ew", padx=12)
        ttk.Label(self, text="Единица измерения").grid(row=4, column=0, sticky="w", padx=12, pady=(10, 4))
        ttk.Entry(self, textvariable=self.unit_var, width=30).grid(row=5, column=0, sticky="ew", padx=12)
        ttk.Label(self, text="Измерения через пробел, запятую или перевод строки").grid(row=6, column=0, sticky="w", padx=12, pady=(10, 4))
        self.measurements_text.grid(row=7, column=0, padx=12, pady=(0, 10))
        self.measurements_text.insert("1.0", ", ".join(format(value, ".6g") for value in initial_measurements))

        buttons = ttk.Frame(self)
        buttons.grid(row=8, column=0, sticky="e", padx=12, pady=(0, 12))
        ttk.Button(buttons, text="Сохранить", command=self._save).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Отмена", command=self.destroy).grid(row=0, column=1)
        self.columnconfigure(0, weight=1)

    def _save(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите имя переменной.", parent=self)
            return

        try:
            instrumental_error = float(self.instrumental_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Ошибка", "Инструментальная погрешность должна быть числом.", parent=self)
            return

        raw_text = self.measurements_text.get("1.0", "end").replace("\n", " ").replace(";", " ").replace(",", " ")
        try:
            measurements = [float(chunk) for chunk in raw_text.split() if chunk]
        except ValueError:
            messagebox.showerror("Ошибка", "Измерения должны содержать только числа.", parent=self)
            return

        if not measurements:
            messagebox.showerror("Ошибка", "Нужно указать хотя бы одно измерение.", parent=self)
            return

        self.result = {
            "name": name,
            "instrumental_error": instrumental_error,
            "unit": self.unit_var.get().strip(),
            "measurements": measurements,
        }
        self.destroy()


def main() -> None:
    app = MeasurementApp()
    app.mainloop()


if __name__ == "__main__":
    main()
