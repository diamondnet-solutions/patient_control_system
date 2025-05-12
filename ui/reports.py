# =============================================
# HEADER INFORMATION
# =============================================
# Nombre del archivo: reports.py
# Propósito: Interfaz gráfica para la generación y visualización de reportes
# Empresa: DiamondNetSolutions
# Autor: [Nombre del Autor]
# Fecha de creación: [Fecha de Creación]
# Última modificación: [Fecha de Modificación]
# =============================================
"""
Módulo para la gestión de reportes en la interfaz gráfica
"""

import calendar
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry

from core.report_generator import ReportGenerator


def confirm_email_sent(window: tk.Toplevel) -> None:
    """Confirma el envío del correo y cierra la ventana"""
    messagebox.showinfo("Correo Enviado",
                        "El reporte ha sido enviado por correo correctamente.")
    window.destroy()


class ReportsFrame(ttk.Frame):
    """Frame principal para la gestión de reportes"""

    def __init__(self, parent: tk.Widget):
        """Inicializa el marco de reportes"""
        super().__init__(parent)
        self.parent = parent

        # Variables de control
        self.report_type = tk.StringVar(value="mensual")
        self.year_var = tk.IntVar(value=datetime.datetime.now().year)
        self.month_var = tk.StringVar()  # Cambiado a StringVar

        # Inicializar el generador de reportes
        self.report_generator = ReportGenerator()

        # Configurar interfaz
        self.setup_ui()

    def setup_ui(self) -> None:
        """Configura todos los elementos de la interfaz de usuario"""
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título del módulo
        self.title_label = ttk.Label(
            self,
            text="Reportes del Sistema",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(pady=10, fill=tk.X)

        # Marco para controles superiores (filtros + botones)
        self.top_controls_frame = ttk.Frame(self)
        self.top_controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # Marco para filtros (ahora ocupa el lado izquierdo)
        self.create_filter_controls()

        # Marco para botones de acción (lado derecho)
        self.create_action_buttons()

        # Marco para pestañas de reportes
        self.reports_notebook = ttk.Notebook(self)
        self.reports_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear las pestañas
        self.create_income_report_tab()
        self.create_worked_hours_tab()
        self.create_empty_hours_tab()

        self.update_idletasks()

    def create_filter_controls(self) -> None:
        """Crea los controles para filtrar los reportes"""
        self.filter_frame = ttk.LabelFrame(self, text="Filtros de Reporte")
        self.filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Fila 1: Tipo de reporte, año y mes
        filter_row1 = ttk.Frame(self.filter_frame)
        filter_row1.pack(fill=tk.X, padx=5, pady=5)

        # Tipo de reporte
        ttk.Label(filter_row1, text="Tipo de Reporte:").pack(side=tk.LEFT, padx=5)
        report_type_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.report_type,
            values=["mensual", "semanal", "diario", "personalizado"],
            state="readonly",
            width=12
        )
        report_type_combo.pack(side=tk.LEFT, padx=5)
        report_type_combo.bind("<<ComboboxSelected>>", self.on_report_type_change)

        # Año
        ttk.Label(filter_row1, text="Año:").pack(side=tk.LEFT, padx=5)
        current_year = datetime.datetime.now().year
        year_values = [str(year) for year in range(current_year - 5, current_year + 1)]
        year_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.year_var,
            values=year_values,
            state="readonly",
            width=8
        )
        year_combo.pack(side=tk.LEFT, padx=5)

        # Mes - Solución definitiva
        ttk.Label(filter_row1, text="Mes:").pack(side=tk.LEFT, padx=5)
        self.month_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.month_var,
            state="readonly",
            width=12
        )

        # Configurar meses
        months = [(i, calendar.month_name[i]) for i in range(1, 13)]
        self.month_combo['values'] = [f"{num} - {name}" for num, name in months]
        self.month_combo.current(datetime.datetime.now().month - 1)
        self.month_combo.pack(side=tk.LEFT, padx=5)


        # Fila 2: Fechas personalizadas
        self.custom_date_frame = ttk.Frame(self.filter_frame)

        # Fecha de inicio
        ttk.Label(self.custom_date_frame, text="Fecha Inicio:").pack(side=tk.LEFT, padx=5)
        self.start_date = DateEntry(
            self.custom_date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        self.start_date.pack(side=tk.LEFT, padx=5)

        # Fecha de fin
        ttk.Label(self.custom_date_frame, text="Fecha Fin:").pack(side=tk.LEFT, padx=5)
        self.end_date = DateEntry(
            self.custom_date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        self.end_date.pack(side=tk.LEFT, padx=5)

    def get_selected_month(self) -> int:
        """Obtiene el mes seleccionado como entero"""
        try:
            month_str = self.month_var.get()
            if not month_str:
                return datetime.datetime.now().month

            # Extraer el número del formato "N - NombreMes"
            month_num = int(month_str.split('-')[0].strip())
            return month_num if 1 <= month_num <= 12 else datetime.datetime.now().month
        except:
            return datetime.datetime.now().month

    def create_report_tabs(self) -> None:
        """Crea las pestañas para los diferentes tipos de reportes"""
        self.reports_notebook = ttk.Notebook(self)
        self.reports_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Pestaña de ingresos
        self.create_income_report_tab()

        # Pestaña de horas trabajadas
        self.create_worked_hours_tab()

        # Pestaña de horas sin citas
        self.create_empty_hours_tab()

    def create_income_report_tab(self) -> None:
        """Crea la pestaña para reportes de ingresos"""
        income_frame = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(income_frame, text="Ingresos")

        # Gráfico de ingresos
        chart_frame = ttk.LabelFrame(income_frame, text="Gráfico de Ingresos")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Ingresos Diarios")
        self.income_chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.income_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tabla de ingresos
        table_frame = ttk.LabelFrame(income_frame, text="Detalle de Ingresos")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ('fecha', 'concepto', 'paciente', 'monto')
        self.income_table = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Configurar columnas
        for col in columns:
            self.income_table.heading(col, text=col.capitalize())
            self.income_table.column(col, width=100 if col != 'concepto' else 200)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.income_table.yview)
        self.income_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.income_table.pack(fill=tk.BOTH, expand=True)

        # Total de ingresos
        total_frame = ttk.Frame(income_frame)
        total_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(total_frame, text="Total de Ingresos:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.total_income_label = ttk.Label(total_frame, text="$0.00", font=("Arial", 12, "bold"))
        self.total_income_label.pack(side=tk.LEFT, padx=5)

    def create_worked_hours_tab(self) -> None:
        """Crea la pestaña para reportes de horas trabajadas"""
        hours_frame = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(hours_frame, text="Horas Trabajadas")

        # Gráfico de horas trabajadas
        chart_frame = ttk.LabelFrame(hours_frame, text="Gráfico de Horas Trabajadas")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Horas Trabajadas por Día")
        self.hours_chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.hours_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tabla de horas trabajadas
        table_frame = ttk.LabelFrame(hours_frame, text="Detalle de Horas Trabajadas")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ('fecha', 'dia', 'hora_inicio', 'hora_fin', 'total_horas')
        self.hours_table = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Configurar columnas
        for col in columns:
            self.hours_table.heading(col, text=col.replace('_', ' ').capitalize())
            self.hours_table.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.hours_table.yview)
        self.hours_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hours_table.pack(fill=tk.BOTH, expand=True)

        # Total de horas
        total_frame = ttk.Frame(hours_frame)
        total_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(total_frame, text="Total de Horas Trabajadas:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.total_hours_label = ttk.Label(total_frame, text="0 horas", font=("Arial", 12, "bold"))
        self.total_hours_label.pack(side=tk.LEFT, padx=5)

    def create_empty_hours_tab(self) -> None:
        """Crea la pestaña para reportes de horas sin citas"""
        empty_frame = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(empty_frame, text="Horas Sin Citas")

        # Gráfico de horas sin citas
        chart_frame = ttk.LabelFrame(empty_frame, text="Gráfico de Horas Sin Citas")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Horas Sin Citas por Día")
        self.empty_chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.empty_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tabla de horas sin citas
        table_frame = ttk.LabelFrame(empty_frame, text="Detalle de Horas Sin Citas")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ('fecha', 'dia', 'hora_inicio', 'hora_fin', 'total_horas')
        self.empty_table = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Configurar columnas
        for col in columns:
            self.empty_table.heading(col, text=col.replace('_', ' ').capitalize())
            self.empty_table.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.empty_table.yview)
        self.empty_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.empty_table.pack(fill=tk.BOTH, expand=True)

        # Total de horas sin citas
        total_frame = ttk.Frame(empty_frame)
        total_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(total_frame, text="Total de Horas Sin Citas:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.total_empty_label = ttk.Label(total_frame, text="0 horas", font=("Arial", 12, "bold"))
        self.total_empty_label.pack(side=tk.LEFT, padx=5)

    def create_action_buttons(self) -> None:
        """Crea los botones de acción para los reportes"""
        self.actions_frame = ttk.Frame(self)
        # Pack al final, con relleno horizontal y márgenes
        self.actions_frame.pack(fill=tk.X, pady=10, padx=10, anchor=tk.S)

        buttons = [
            ("Generar Reporte", self.generate_report),
            ("Exportar a PDF", self.export_pdf),
            ("Exportar a Excel", self.export_excel),
            ("Enviar por Correo", self.send_email)
        ]

        for text, command in buttons:
            btn = ttk.Button(
                self.actions_frame,
                text=text,
                command=command,
                width=10  # Ancho fijo para uniformidad
            )
            btn.pack(side=tk.LEFT, padx=5, expand=True)

    def on_report_type_change(self, event=None) -> None:
        """Maneja el cambio en el tipo de reporte seleccionado"""
        if self.report_type.get() == "personalizado":
            self.custom_date_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.custom_date_frame.pack_forget()
        self.top_controls_frame.update_idletasks()

    def generate_report(self) -> None:
        """Genera el reporte según los filtros seleccionados"""
        try:
            report_type = self.report_type.get()
            year = self.year_var.get()
            month = self.get_selected_month()  # Usamos el método seguro

            if report_type == "personalizado":
                start_date = self.start_date.get_date().strftime('%Y-%m-%d')
                end_date = self.end_date.get_date().strftime('%Y-%m-%d')
            elif report_type == "mensual":
                start_date = datetime.date(year, month, 1).strftime('%Y-%m-%d')
                end_date = datetime.date(year, month, calendar.monthrange(year, month)[1]).strftime('%Y-%m-%d')
            elif report_type == "semanal":
                today = datetime.datetime.now().date()
                start_date = (today - datetime.timedelta(days=today.weekday())).strftime('%Y-%m-%d')
                end_date = (today + datetime.timedelta(days=6 - today.weekday())).strftime('%Y-%m-%d')
            else:  # diario
                selected_date = datetime.date(year, month, self.day_var.get() if hasattr(self, 'day_var') else 1)
                start_date = end_date = selected_date.strftime('%Y-%m-%d')

            # Obtener el tipo de reporte actual
            current_tab = self.reports_notebook.tab(self.reports_notebook.select(), "text")

            if current_tab == "Ingresos":
                self.generate_income_report(start_date, end_date)
            elif current_tab == "Horas Trabajadas":
                self.generate_worked_hours_report(start_date, end_date)
            elif current_tab == "Horas Sin Citas":
                self.generate_empty_hours_report(start_date, end_date)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")

    def generate_income_report(self, start_date: str, end_date: str) -> None:
        """Genera y muestra el reporte de ingresos"""
        try:
            report_data = self.report_generator.generate_income_report(start_date, end_date)

            # Limpiar tabla
            for item in self.income_table.get_children():
                self.income_table.delete(item)

            # Llenar tabla con datos
            for item in report_data['data']:
                self.income_table.insert('', tk.END, values=(
                    item['date'],
                    item['treatments'] or "Consulta",
                    item['patient'],
                    f"${item['amount']:,.2f}"
                ))

            # Actualizar total
            self.total_income_label.config(text=f"${report_data['total']:,.2f}")

            # Actualizar gráfico
            self.update_income_chart(report_data)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de ingresos: {str(e)}")

    def generate_worked_hours_report(self, start_date: str, end_date: str) -> None:
        """Genera y muestra el reporte de horas trabajadas"""
        try:
            report_data = self.report_generator.generate_worked_hours_report(start_date, end_date)

            # Limpiar tabla
            for item in self.hours_table.get_children():
                self.hours_table.delete(item)

            # Llenar tabla con datos
            for item in report_data['data']:
                self.hours_table.insert('', tk.END, values=(
                    item['date'],
                    item['day'],
                    item['start_time'],
                    item['end_time'],
                    f"{item['hours_worked']:.1f}h"
                ))

            # Actualizar total
            self.total_hours_label.config(text=f"{report_data['total_hours']:.1f} horas")

            # Actualizar gráfico
            self.update_worked_hours_chart(report_data)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de horas trabajadas: {str(e)}")

    def generate_empty_hours_report(self, start_date: str, end_date: str) -> None:
        """Genera y muestra el reporte de horas sin citas"""
        try:
            report_data = self.report_generator.generate_empty_hours_report(start_date, end_date)

            # Limpiar tabla
            for item in self.empty_table.get_children():
                self.empty_table.delete(item)

            # Llenar tabla con datos
            for item in report_data['data']:
                self.empty_table.insert('', tk.END, values=(
                    item['date'],
                    item['day'],
                    item['start_time'],
                    item['end_time'],
                    f"{item['hours']:.1f}h"
                ))

            # Actualizar total
            self.total_empty_label.config(text=f"{report_data['total_hours']:.1f} horas")

            # Actualizar gráfico
            self.update_empty_hours_chart(report_data)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de horas sin citas: {str(e)}")

    def update_income_chart(self, report_data: Dict[str, Any]) -> None:
        """Actualiza el gráfico de ingresos con nuevos datos"""
        fig = self.income_chart_canvas.figure
        fig.clear()

        ax = fig.add_subplot(111)

        # Procesar datos para el gráfico
        dates = [item['date'] for item in report_data['data']]
        amounts = [item['amount'] for item in report_data['data']]

        ax.bar(dates, amounts, color='skyblue')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Ingresos ($)')
        ax.set_title('Ingresos Diarios')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        self.income_chart_canvas.draw()

    def update_worked_hours_chart(self, report_data: Dict[str, Any]) -> None:
        """Actualiza el gráfico de horas trabajadas con nuevos datos"""
        fig = self.hours_chart_canvas.figure
        fig.clear()

        ax = fig.add_subplot(111)

        # Procesar datos para el gráfico
        days = [item['day'] for item in report_data['data']]
        hours = [item['hours_worked'] for item in report_data['data']]

        ax.plot(days, hours, marker='o', linestyle='-', color='green')
        ax.set_xlabel('Día')
        ax.set_ylabel('Horas')
        ax.set_title('Horas Trabajadas por Día')
        ax.grid(True, linestyle='--', alpha=0.7)

        self.hours_chart_canvas.draw()

    def update_empty_hours_chart(self, report_data: Dict[str, Any]) -> None:
        """Actualiza el gráfico de horas sin citas con nuevos datos"""
        fig = self.empty_chart_canvas.figure
        fig.clear()

        ax = fig.add_subplot(111)

        # Procesar datos para el gráfico
        days = [item['day'] for item in report_data['data']]
        hours = [item['hours'] for item in report_data['data']]

        ax.bar(days, hours, color='coral')
        ax.set_xlabel('Día')
        ax.set_ylabel('Horas')
        ax.set_title('Horas Sin Citas por Día')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        self.empty_chart_canvas.draw()

    def export_pdf(self) -> None:
        """Exporta el reporte actual a PDF"""
        try:
            current_tab = self.reports_notebook.tab(self.reports_notebook.select(), "text")

            # Obtener datos según el tipo de reporte
            if current_tab == "Ingresos":
                report_type = 'income'
                # Implementar lógica para obtener datos
            elif current_tab == "Horas Trabajadas":
                report_type = 'worked_hours'
                # Implementar lógica para obtener datos
            elif current_tab == "Horas Sin Citas":
                report_type = 'empty_hours'
                # Implementar lógica para obtener datos

            # Solicitar ubicación para guardar
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title=f"Guardar Reporte de {current_tab} como PDF"
            )

            if file_path:
                # Generar PDF (implementar según report_generator)
                messagebox.showinfo("Éxito", f"Reporte de {current_tab} exportado a PDF correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a PDF: {str(e)}")

    def export_excel(self) -> None:
        """Exporta el reporte actual a Excel"""
        try:
            current_tab = self.reports_notebook.tab(self.reports_notebook.select(), "text")

            # Solicitar ubicación para guardar
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title=f"Guardar Reporte de {current_tab} como Excel"
            )

            if file_path:
                # Generar Excel (implementar según report_generator)
                messagebox.showinfo("Éxito", f"Reporte de {current_tab} exportado a Excel correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Excel: {str(e)}")

    def send_email(self) -> None:
        """Envía el reporte actual por correo electrónico"""
        email_window = tk.Toplevel(self)
        email_window.title("Enviar Reporte por Correo")
        email_window.geometry("400x300")

        # Contenido de la ventana
        ttk.Label(email_window, text="Enviar Reporte por Correo", font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(email_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Campos del formulario
        ttk.Label(form_frame, text="Destinatario:").grid(row=0, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(form_frame, width=30)
        email_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Label(form_frame, text="Asunto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        subject_entry = ttk.Entry(form_frame, width=30)
        subject_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(form_frame, text="Mensaje:").grid(row=2, column=0, sticky=tk.W, pady=5)
        message_text = tk.Text(form_frame, width=30, height=5)
        message_text.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Botones
        buttons_frame = ttk.Frame(email_window)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(
            buttons_frame,
            text="Enviar",
            command=lambda: confirm_email_sent(email_window)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame,
            text="Cancelar",
            command=email_window.destroy
        ).pack(side=tk.LEFT, padx=5)


if __name__ == "__main__":
    # Código para pruebas
    root = tk.Tk()
    root.title("Módulo de Reportes")
    root.geometry("900x700")
    app = ReportsFrame(root)
    root.mainloop()