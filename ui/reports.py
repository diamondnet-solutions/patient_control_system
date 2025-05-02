#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para la gestión de reportes
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import calendar
import datetime
from tkcalendar import DateEntry
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd


class ReportsFrame(ttk.Frame):
    def __init__(self, parent):
        """Inicializa el marco de reportes"""
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)

        # Título del módulo
        self.title_label = ttk.Label(self, text="Reportes del Sistema",
                                     font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        # Marco para filtros
        self.filter_frame = ttk.LabelFrame(self, text="Filtros de Reporte")
        self.filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Crear controles de filtro
        self.create_filter_controls()

        # Marco para pestañas de tipos de reportes
        self.reports_notebook = ttk.Notebook(self)
        self.reports_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear páginas para cada tipo de reporte
        self.create_income_report_tab()
        self.create_worked_hours_tab()
        self.create_empty_hours_tab()

        # Marco para botones de acciones
        self.actions_frame = ttk.Frame(self)
        self.actions_frame.pack(fill=tk.X, padx=10, pady=10)

        # Botones de acción
        self.create_action_buttons()

    def create_filter_controls(self):
        """Crea controles para filtrar los reportes"""
        # Marco para la primera fila de filtros
        filter_row1 = ttk.Frame(self.filter_frame)
        filter_row1.pack(fill=tk.X, padx=5, pady=5)

        # Tipo de reporte
        ttk.Label(filter_row1, text="Tipo de Reporte:").pack(side=tk.LEFT, padx=5)
        self.report_type = tk.StringVar(value="mensual")
        report_type_combo = ttk.Combobox(filter_row1, textvariable=self.report_type,
                                         values=["mensual", "semanal", "diario", "personalizado"],
                                         state="readonly", width=15)
        report_type_combo.pack(side=tk.LEFT, padx=5)
        report_type_combo.bind("<<ComboboxSelected>>", self.on_report_type_change)

        # Año
        ttk.Label(filter_row1, text="Año:").pack(side=tk.LEFT, padx=5)
        current_year = datetime.datetime.now().year
        self.year_var = tk.IntVar(value=current_year)
        year_values = [str(year) for year in range(current_year - 5, current_year + 1)]
        year_combo = ttk.Combobox(filter_row1, textvariable=self.year_var,
                                  values=year_values, state="readonly", width=10)
        year_combo.pack(side=tk.LEFT, padx=5)

        # Mes
        ttk.Label(filter_row1, text="Mes:").pack(side=tk.LEFT, padx=5)
        current_month = datetime.datetime.now().month
        self.month_var = tk.IntVar(value=current_month)
        month_values = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
        self.month_combo = ttk.Combobox(filter_row1, textvariable=self.month_var,
                                        values=[f"{i} - {name}" for i, name in month_values],
                                        state="readonly", width=15)
        self.month_combo.current(current_month - 1)
        self.month_combo.pack(side=tk.LEFT, padx=5)

        # Marco para la segunda fila de filtros (fecha personalizada)
        self.custom_date_frame = ttk.Frame(self.filter_frame)

        # Fecha de inicio
        ttk.Label(self.custom_date_frame, text="Fecha Inicio:").pack(side=tk.LEFT, padx=5)
        self.start_date = DateEntry(self.custom_date_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        self.start_date.pack(side=tk.LEFT, padx=5)

        # Fecha de fin
        ttk.Label(self.custom_date_frame, text="Fecha Fin:").pack(side=tk.LEFT, padx=5)
        self.end_date = DateEntry(self.custom_date_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.end_date.pack(side=tk.LEFT, padx=5)

    def on_report_type_change(self, event=None):
        """Maneja el cambio en el tipo de reporte"""
        if self.report_type.get() == "personalizado":
            self.custom_date_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.custom_date_frame.pack_forget()

    def create_income_report_tab(self):
        """Crea la pestaña para reportes de ingresos"""
        income_frame = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(income_frame, text="Ingresos")

        # Marco para gráfica
        chart_frame = ttk.LabelFrame(income_frame, text="Gráfico de Ingresos")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear figura para el gráfico de ejemplo
        fig, ax = plt.subplots(figsize=(8, 4))

        # Datos de ejemplo para el gráfico
        dates = ['01/04', '02/04', '03/04', '04/04', '05/04']
        incomes = [1200, 1500, 800, 2000, 1300]

        # Crear gráfico de barras
        ax.bar(dates, incomes, color='skyblue')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Ingresos ($)')
        ax.set_title('Ingresos Diarios')

        # Crear canvas para mostrar el gráfico en Tkinter
        self.income_chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.income_chart_canvas.draw()
        self.income_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Marco para tabla de datos
        table_frame = ttk.LabelFrame(income_frame, text="Detalle de Ingresos")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear tabla para datos
        columns = ('fecha', 'concepto', 'paciente', 'monto')
        self.income_table = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Configurar columnas
        self.income_table.heading('fecha', text='Fecha')
        self.income_table.heading('concepto', text='Concepto')
        self.income_table.heading('paciente', text='Paciente')
        self.income_table.heading('monto', text='Monto ($)')

        self.income_table.column('fecha', width=100)
        self.income_table.column('concepto', width=200)
        self.income_table.column('paciente', width=150)
        self.income_table.column('monto', width=100)

        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.income_table.yview)
        self.income_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.income_table.pack(fill=tk.BOTH, expand=True)

        # Añadir datos de ejemplo
        example_data = [
            ('01/04/2025', 'Consulta general', 'Juan Pérez', '$300'),
            ('01/04/2025', 'Tratamiento dental', 'María González', '$900'),
            ('02/04/2025', 'Consulta general', 'Roberto Sánchez', '$300'),
            ('02/04/2025', 'Limpieza dental', 'Ana López', '$400'),
            ('02/04/2025', 'Extracción', 'Pedro Ramírez', '$800'),
            ('03/04/2025', 'Consulta general', 'Laura Torres', '$300'),
            ('03/04/2025', 'Tratamiento dental', 'Carlos Ruiz', '$500'),
            ('04/04/2025', 'Consulta general', 'Diana Flores', '$300'),
            ('04/04/2025', 'Ortodoncia', 'José Martínez', '$1700'),
            ('05/04/2025', 'Consulta general', 'Sofía Castro', '$300'),
            ('05/04/2025', 'Limpieza dental', 'Fernando Gómez', '$400'),
            ('05/04/2025', 'Tratamiento dental', 'Patricia Díaz', '$600'),
        ]

        for item in example_data:
            self.income_table.insert('', tk.END, values=item)

        # Etiqueta para mostrar el total
        total_frame = ttk.Frame(income_frame)
        total_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(total_frame, text="Total de Ingresos:",
                  font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)

        self.total_income_label = ttk.Label(total_frame, text="$6,800.00",
                                            font=("Arial", 12, "bold"))
        self.total_income_label.pack(side=tk.LEFT, padx=5)

    def create_worked_hours_tab(self):
        """Crea la pestaña para reportes de horas trabajadas"""
        hours_frame = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(hours_frame, text="Horas Trabajadas")

        # Marco para gráfica
        chart_frame = ttk.LabelFrame(hours_frame, text="Gráfico de Horas Trabajadas")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear figura para el gráfico de ejemplo
        fig, ax = plt.subplots(figsize=(8, 4))

        # Datos de ejemplo para el gráfico
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        hours = [8, 7, 9, 6, 8]

        # Crear gráfico de líneas
        ax.plot(days, hours, marker='o', linestyle='-', color='green')
        ax.set_xlabel('Día')
        ax.set_ylabel('Horas')
        ax.set_title('Horas Trabajadas por Día')
        ax.grid(True, linestyle='--', alpha=0.7)

        # Crear canvas para mostrar el gráfico en Tkinter
        self.hours_chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.hours_chart_canvas.draw()
        self.hours_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Marco para tabla de datos
        table_frame = ttk.LabelFrame(hours_frame, text="Detalle de Horas Trabajadas")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear tabla para datos
        columns = ('fecha', 'dia', 'hora_inicio', 'hora_fin', 'total_horas')
        self.hours_table = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Configurar columnas
        self.hours_table.heading('fecha', text='Fecha')
        self.hours_table.heading('dia', text='Día')
        self.hours_table.heading('hora_inicio', text='Hora Inicio')
        self.hours_table.heading('hora_fin', text='Hora Fin')
        self.hours_table.heading('total_horas', text='Total Horas')

        self.hours_table.column('fecha', width=100)
        self.hours_table.column('dia', width=100)
        self.hours_table.column('hora_inicio', width=100)
        self.hours_table.column('hora_fin', width=100)
        self.hours_table.column('total_horas', width=100)

        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.hours_table.yview)
        self.hours_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hours_table.pack(fill=tk.BOTH, expand=True)

        # Añadir datos de ejemplo
        example_data = [
            ('01/04/2025', 'Lunes', '09:00', '17:00', '8h'),
            ('02/04/2025', 'Martes', '09:30', '16:30', '7h'),
            ('03/04/2025', 'Miércoles', '08:00', '17:00', '9h'),
            ('04/04/2025', 'Jueves', '10:00', '16:00', '6h'),
            ('05/04/2025', 'Viernes', '09:00', '17:00', '8h'),
        ]

        for item in example_data:
            self.hours_table.insert('', tk.END, values=item)

        # Etiqueta para mostrar el total
        total_frame = ttk.Frame(hours_frame)
        total_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(total_frame, text="Total de Horas Trabajadas:",
                  font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)

        self.total_hours_label = ttk.Label(total_frame, text="38 horas",
                                           font=("Arial", 12, "bold"))
        self.total_hours_label.pack(side=tk.LEFT, padx=5)

    def create_empty_hours_tab(self):
        """Crea la pestaña para reportes de horas sin citas"""
        empty_frame = ttk.Frame(self.reports_notebook)
        self.reports_notebook.add(empty_frame, text="Horas Sin Citas")

        # Marco para gráfica
        chart_frame = ttk.LabelFrame(empty_frame, text="Gráfico de Horas Sin Citas")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear figura para el gráfico de ejemplo
        fig, ax = plt.subplots(figsize=(8, 4))

        # Datos de ejemplo para el gráfico
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        empty_hours = [2, 3, 1, 4, 2]

        # Crear gráfico de barras
        ax.bar(days, empty_hours, color='coral')
        ax.set_xlabel('Día')
        ax.set_ylabel('Horas')
        ax.set_title('Horas Sin Citas por Día')

        # Crear canvas para mostrar el gráfico en Tkinter
        self.empty_chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.empty_chart_canvas.draw()
        self.empty_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Marco para tabla de datos
        table_frame = ttk.LabelFrame(empty_frame, text="Detalle de Horas Sin Citas")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear tabla para datos
        columns = ('fecha', 'dia', 'hora_inicio', 'hora_fin', 'total_horas')
        self.empty_table = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Configurar columnas
        self.empty_table.heading('fecha', text='Fecha')
        self.empty_table.heading('dia', text='Día')
        self.empty_table.heading('hora_inicio', text='Hora Inicio')
        self.empty_table.heading('hora_fin', text='Hora Fin')
        self.empty_table.heading('total_horas', text='Total Horas')

        self.empty_table.column('fecha', width=100)
        self.empty_table.column('dia', width=100)
        self.empty_table.column('hora_inicio', width=100)
        self.empty_table.column('hora_fin', width=100)
        self.empty_table.column('total_horas', width=100)

        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.empty_table.yview)
        self.empty_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.empty_table.pack(fill=tk.BOTH, expand=True)

        # Añadir datos de ejemplo
        example_data = [
            ('01/04/2025', 'Lunes', '13:00', '14:00', '1h'),
            ('01/04/2025', 'Lunes', '16:00', '17:00', '1h'),
            ('02/04/2025', 'Martes', '10:00', '11:00', '1h'),
            ('02/04/2025', 'Martes', '15:00', '17:00', '2h'),
            ('03/04/2025', 'Miércoles', '12:00', '13:00', '1h'),
            ('04/04/2025', 'Jueves', '09:00', '10:00', '1h'),
            ('04/04/2025', 'Jueves', '11:00', '12:00', '1h'),
            ('04/04/2025', 'Jueves', '14:00', '16:00', '2h'),
            ('05/04/2025', 'Viernes', '09:00', '10:00', '1h'),
            ('05/04/2025', 'Viernes', '14:00', '15:00', '1h'),
        ]

        for item in example_data:
            self.empty_table.insert('', tk.END, values=item)

        # Etiqueta para mostrar el total
        total_frame = ttk.Frame(empty_frame)
        total_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(total_frame, text="Total de Horas Sin Citas:",
                  font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)

        self.total_empty_label = ttk.Label(total_frame, text="12 horas",
                                           font=("Arial", 12, "bold"))
        self.total_empty_label.pack(side=tk.LEFT, padx=5)

    def create_action_buttons(self):
        """Crea los botones de acción para reportes"""
        # Botón para generar reporte
        self.generate_btn = ttk.Button(self.actions_frame, text="Generar Reporte",
                                       command=self.generate_report)
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        # Botón para exportar a PDF
        self.export_pdf_btn = ttk.Button(self.actions_frame, text="Exportar a PDF",
                                         command=self.export_pdf)
        self.export_pdf_btn.pack(side=tk.LEFT, padx=5)

        # Botón para exportar a Excel
        self.export_excel_btn = ttk.Button(self.actions_frame, text="Exportar a Excel",
                                           command=self.export_excel)
        self.export_excel_btn.pack(side=tk.LEFT, padx=5)

        # Botón para enviar por correo
        self.email_btn = ttk.Button(self.actions_frame, text="Enviar por Correo",
                                    command=self.send_email)
        self.email_btn.pack(side=tk.LEFT, padx=5)

    def generate_report(self):
        """Genera el reporte según los filtros seleccionados"""
        # Aquí se implementaría la lógica real para generar reportes
        # desde la base de datos o archivos

        # Por ahora, solo mostramos un mensaje
        report_type = self.report_type.get()
        year = self.year_var.get()

        if report_type == "personalizado":
            start = self.start_date.get_date()
            end = self.end_date.get_date()
            period = f"desde {start.strftime('%d/%m/%Y')} hasta {end.strftime('%d/%m/%Y')}"
        elif report_type == "mensual":
            month = self.month_var.get()
            period = f"del mes {calendar.month_name[month]} de {year}"
        elif report_type == "semanal":
            period = f"de la semana actual de {year}"
        else:  # diario
            period = f"del día de hoy"

        # Mensaje de confirmación
        current_tab = self.reports_notebook.tab(self.reports_notebook.select(), "text")
        messagebox.showinfo("Reporte Generado",
                            f"Se ha generado el reporte {report_type} de {current_tab} {period}.")

    def export_pdf(self):
        """Exporta el reporte actual a PDF"""
        # Aquí se implementaría la generación de un archivo PDF

        # Por ahora, simulamos la exportación
        current_tab = self.reports_notebook.tab(self.reports_notebook.select(), "text")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title=f"Guardar Reporte de {current_tab} como PDF"
        )

        if file_path:
            # Aquí se implementaría la generación real del PDF
            messagebox.showinfo("Exportación Exitosa",
                                f"El reporte de {current_tab} ha sido exportado a PDF correctamente.")

    def export_excel(self):
        """Exporta el reporte actual a Excel"""
        # Aquí se implementaría la generación de un archivo Excel

        # Por ahora, simulamos la exportación
        current_tab = self.reports_notebook.tab(self.reports_notebook.select(), "text")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title=f"Guardar Reporte de {current_tab} como Excel"
        )

        if file_path:
            # Aquí se implementaría la generación real del Excel
            messagebox.showinfo("Exportación Exitosa",
                                f"El reporte de {current_tab} ha sido exportado a Excel correctamente.")

    def send_email(self):
        """Envía el reporte por correo electrónico"""
        # Aquí se implementaría la lógica de envío de correo

        # Por ahora, simulamos el envío
        email_window = tk.Toplevel(self)
        email_window.title("Enviar Reporte por Correo")
        email_window.geometry("400x300")

        # Contenido de la ventana de correo
        ttk.Label(email_window, text="Enviar Reporte por Correo",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(email_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

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

        ttk.Button(buttons_frame, text="Enviar",
                   command=lambda: self.confirm_email_sent(email_window)).pack(side=tk.LEFT, padx=5)

        ttk.Button(buttons_frame, text="Cancelar",
                   command=email_window.destroy).pack(side=tk.LEFT, padx=5)

    def confirm_email_sent(self, window):
        """Confirma el envío del correo y cierra la ventana"""
        messagebox.showinfo("Correo Enviado",
                            "El reporte ha sido enviado por correo correctamente.")
        window.destroy()


if __name__ == "__main__":
    # Código para pruebas
    root = tk.Tk()
    root.title("Módulo de Reportes")
    root.geometry("900x700")
    app = ReportsFrame(root)
    root.mainloop()