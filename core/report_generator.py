# =============================================
# HEADER INFORMATION
# =============================================
# Nombre del archivo: report_generator.py
# Propósito: Generación de reportes mensuales (ingresos, horas trabajadas, horas sin citas)
# Empresa: DiamondNetSolutions
# Autor: [Nombre del Autor]
# Fecha de creación: [Fecha de Creación]
# Última modificación: [Fecha de Modificación]
# =============================================
"""
Módulo para la generación de reportes del sistema de control de pacientes.
Permite generar reportes de ingresos, horas trabajadas y horas sin citas.
"""

# =============================================
# LIBRERÍAS
# =============================================
# Librerías estándar de Python
import os
import sys
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Union, Any
import calendar
import io

# Librerías de terceros
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF

# Librerías propias del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import DatabaseManager


def export_to_excel(
        report_data: Dict[str, Any],
        report_type: str
) -> bytes:
    """
    Exporta el reporte a formato Excel.

    Args:
        report_data (dict): Datos del reporte a exportar
        report_type (str): Tipo de reporte ('income', 'worked_hours', 'empty_hours')

    Returns:
        bytes: Contenido del archivo Excel generado
    """
    output = io.BytesIO()

    if report_type == 'income':
        df = pd.DataFrame(report_data['data'])
        df['amount'] = df['amount'].apply(lambda x: f"${x:,.2f}")

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Ingresos', index=False)

            # Formato adicional
            workbook = writer.book
            worksheet = writer.sheets['Ingresos']

            # Formato de moneda
            money_format = workbook.add_format({'num_format': '$#,##0.00'})
            worksheet.set_column('D:D', 15, money_format)

            # Total
            worksheet.write(len(df) + 1, 0, 'Total:')
            worksheet.write(len(df) + 1, 3, report_data['total'], money_format)

    elif report_type == 'worked_hours':
        # Implementar exportación para horas trabajadas
        pass

    elif report_type == 'empty_hours':
        # Implementar exportación para horas vacías
        pass

    return output.getvalue()


def _generate_date_range(start_date: str, end_date: str) -> List[date]:
    """
    Genera una lista de fechas en el rango especificado.

    Args:
        start_date (str): Fecha de inicio en formato YYYY-MM-DD
        end_date (str): Fecha de fin en formato YYYY-MM-DD

    Returns:
        list: Lista de objetos date
    """
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    date_list = []
    current = start

    while current <= end:
        date_list.append(current)
        current += timedelta(days=1)

    return date_list


def _calculate_empty_slots(
        day: date,
        day_schedule: Dict[str, Any],
        appointments: List[Dict[str, str]],
        slot_duration: int = 60
) -> List[Dict[str, Any]]:
    """
    Calcula los slots vacíos para un día específico.

    Args:
        day (date): Fecha a analizar
        day_schedule (dict): Horario de trabajo para ese día
        appointments (list): Lista de citas para ese día
        slot_duration (int): Duración del slot en minutos (default: 60)

    Returns:
        list: Lista de slots vacíos
    """
    empty_slots = []

    if not day_schedule['is_working_day']:
        return empty_slots

    start_time = datetime.strptime(day_schedule['start_time'], '%H:%M').time()
    end_time = datetime.strptime(day_schedule['end_time'], '%H:%M').time()

    current_time = datetime.combine(day, start_time)
    end_datetime = datetime.combine(day, end_time)

    while current_time + timedelta(minutes=slot_duration) <= end_datetime:
        slot_end = current_time + timedelta(minutes=slot_duration)

        # Verificar si el slot está ocupado
        is_occupied = False
        for appt in appointments:
            appt_start = datetime.strptime(appt['start_time'], '%H:%M').time()
            appt_end = datetime.strptime(appt['end_time'], '%H:%M').time()

            appt_start_dt = datetime.combine(day, appt_start)
            appt_end_dt = datetime.combine(day, appt_end)

            if not (slot_end <= appt_start_dt or current_time >= appt_end_dt):
                is_occupied = True
                break

        if not is_occupied:
            empty_slots.append({
                'date': day.strftime('%Y-%m-%d'),
                'day': day.strftime('%A'),
                'start_time': current_time.time().strftime('%H:%M'),
                'end_time': slot_end.time().strftime('%H:%M'),
                'hours': slot_duration / 60
            })

        current_time = slot_end

    return empty_slots


def _generate_report_chart(
        report_data: Dict[str, Any],
        report_type: str
) -> Optional[bytes]:
    """
    Genera un gráfico para el reporte.

    Args:
        report_data (dict): Datos del reporte
        report_type (str): Tipo de reporte

    Returns:
        bytes: Imagen del gráfico en formato PNG
    """
    plt.switch_backend('Agg')  # Para evitar problemas con GUI

    if report_type == 'income':
        df = pd.DataFrame(report_data['data'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.groupby(df['date'].dt.date)['amount'].sum()

        plt.figure(figsize=(10, 5))
        df.plot(kind='bar', color='skyblue')
        plt.title('Ingresos Diarios')
        plt.xlabel('Fecha')
        plt.ylabel('Monto ($)')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

    elif report_type == 'worked_hours':
        # Implementar gráfico para horas trabajadas
        pass

    elif report_type == 'empty_hours':
        # Implementar gráfico para horas vacías
        pass

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf.read()


def _generate_income_pdf(pdf: FPDF, report_data: Dict[str, Any]):
    """Genera la sección de ingresos para el PDF."""
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalle de Ingresos", ln=1)
    pdf.ln(5)

    # Encabezados de tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 10, "Fecha", 1)
    pdf.cell(70, 10, "Paciente", 1)
    pdf.cell(60, 10, "Tratamientos", 1)
    pdf.cell(30, 10, "Monto", 1, 0, 'R')
    pdf.ln()

    # Datos
    pdf.set_font("Arial", '', 10)
    for row in report_data['data']:
        pdf.cell(40, 10, row['date'], 1)
        pdf.cell(70, 10, row['patient'], 1)
        pdf.cell(60, 10, row['treatments'] or "N/A", 1)
        pdf.cell(30, 10, f"${row['amount']:,.2f}", 1, 0, 'R')
        pdf.ln()

    # Total
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(170, 10, "Total:", 1, 0, 'R')
    pdf.cell(30, 10, f"${report_data['total']:,.2f}", 1, 0, 'R')
    pdf.ln()


class ReportGenerator:
    """
    Clase para generar reportes del sistema.
    Proporciona funcionalidades para:
    - Generar reportes de ingresos mensuales
    - Generar reportes de horas trabajadas
    - Generar reportes de horas sin citas
    - Exportar reportes a PDF y Excel
    """
    def __init__(self, db_manager: DatabaseManager = None):
        """
        Inicializa el generador de reportes.

        Args:
            db_manager (DatabaseManager): Instancia de DatabaseManager (opcional)
        """
        self.db_manager = db_manager or DatabaseManager()


    def generate_income_report(
            self,
            start_date: str,
            end_date: str,
            group_by: str = "day"
    ) -> Dict[str, Union[List[Dict[str, Any]], float]]:
        """
        Genera un reporte de ingresos para el período especificado.

        Args:
            start_date (str): Fecha de inicio en formato YYYY-MM-DD
            end_date (str): Fecha de fin en formato YYYY-MM-DD
            group_by (str): Agrupar por 'day', 'week' o 'month'

        Returns:
            dict: {
                'data': Lista de diccionarios con los datos del reporte,
                'total': Total de ingresos en el período
            }
        """
        query = """
                SELECT a.date, \
                       p.first_name || ' ' || p.last_name  AS patient_name, \
                       GROUP_CONCAT(t.name, ', ')          AS treatments, \
                       SUM(at.price_applied * at.quantity) AS amount
                FROM appointments a \
                         JOIN \
                     patients p ON a.patient_id = p.id \
                         LEFT JOIN \
                     appointment_treatments at \
                ON a.id = at.appointment_id
                    LEFT JOIN
                    treatments t ON at.treatment_id = t.id
                WHERE
                    a.date BETWEEN ? \
                  AND ?
                  AND a.status = 'completed'
                GROUP BY
                    a.id
                ORDER BY
                    a.date \
                """

        params = (start_date, end_date)
        raw_data = self.db_manager.execute_query(query, params, fetch_all=True)

        # Procesar datos para agrupación
        processed_data = []
        total_income = 0.0

        if group_by == "day":
            for row in raw_data:
                processed_data.append({
                    'date': row['date'],
                    'patient': row['patient_name'],
                    'treatments': row['treatments'],
                    'amount': row['amount']
                })
                total_income += row['amount']

        elif group_by == "week":
            # Implementar lógica de agrupación por semana
            pass

        elif group_by == "month":
            # Implementar lógica de agrupación por mes
            pass

        return {
            'data': processed_data,
            'total': total_income
        }


    def generate_worked_hours_report(
            self,
            start_date: str,
            end_date: str,
            doctor_id: Optional[int] = None
    ) -> Dict[str, Union[List[Dict[str, Any]], float]]:
        """
        Genera un reporte de horas trabajadas para el período especificado.

        Args:
            start_date (str): Fecha de inicio en formato YYYY-MM-DD
            end_date (str): Fecha de fin en formato YYYY-MM-DD
            doctor_id (int, optional): ID del doctor para filtrar

        Returns:
            dict: {
                'data': Lista de diccionarios con los datos del reporte,
                'total_hours': Total de horas trabajadas en el período
            }
        """
        query = """
                SELECT a.date, \
                       strftime('%w', a.date)                                               AS day_of_week, \
                       a.start_time, \
                       a.end_time, \
                       (strftime('%s', a.end_time) - strftime('%s', a.start_time)) / 3600.0 AS hours_worked
                FROM appointments a
                WHERE a.date BETWEEN ? AND ?
                  AND a.status = 'completed' \
                """

        params = [start_date, end_date]

        if doctor_id:
            query += " AND a.doctor_id = ?"
            params.append(doctor_id)

        query += " ORDER BY a.date, a.start_time"

        raw_data = self.db_manager.execute_query(query, tuple(params), fetch_all=True)

        processed_data = []
        total_hours = 0.0

        for row in raw_data:
            day_name = calendar.day_name[int(row['day_of_week'])]

            processed_data.append({
                'date': row['date'],
                'day': day_name,
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'hours_worked': row['hours_worked']
            })

            total_hours += row['hours_worked']

        return {
            'data': processed_data,
            'total_hours': total_hours
        }

    def generate_empty_hours_report(
            self,
            start_date: str,
            end_date: str
    ) -> Dict[str, Union[List[Dict[str, Any]], float]]:
        """
        Genera un reporte de horas sin citas para el período especificado.

        Args:
            start_date (str): Fecha de inicio en formato YYYY-MM-DD
            end_date (str): Fecha de fin en formato YYYY-MM-DD

        Returns:
            dict: {
                'data': Lista de diccionarios con los datos del reporte,
                'total_hours': Total de horas sin citas en el período
            }
        """
        # Obtener horario de trabajo configurado
        work_schedule = self._get_work_schedule()

        # Generar rango de fechas
        date_range = _generate_date_range(start_date, end_date)

        # Obtener citas agendadas
        appointments = self._get_appointments_in_range(start_date, end_date)

        # Calcular horas sin citas
        empty_slots = []
        total_empty_hours = 0.0

        for day in date_range:
            day_name = calendar.day_name[day.weekday()]
            day_schedule = work_schedule.get(day_name.lower(), None)

            if not day_schedule or not day_schedule['is_working_day']:
                continue

            # Calcular slots vacíos para este día
            day_empty_slots = _calculate_empty_slots(
                day,
                day_schedule,
                appointments.get(day.strftime('%Y-%m-%d'), []))

            empty_slots.extend(day_empty_slots)
            total_empty_hours += sum(slot['hours'] for slot in day_empty_slots)

        return {
            'data': empty_slots,
            'total_hours': total_empty_hours
        }


    def export_to_pdf(
            self,
            report_data: Dict[str, Any],
            report_type: str,
            title: str
    ) -> bytes:
        """
        Exporta el reporte a formato PDF.

        Args:
            report_data (dict): Datos del reporte a exportar
            report_type (str): Tipo de reporte ('income', 'worked_hours', 'empty_hours')
            title (str): Título del reporte

        Returns:
            bytes: Contenido del PDF generado
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Título del reporte
        pdf.cell(200, 10, txt=title, ln=1, align='C')
        pdf.ln(10)

        # Contenido según tipo de reporte
        if report_type == 'income':
            _generate_income_pdf(pdf, report_data)
        elif report_type == 'worked_hours':
            self._generate_worked_hours_pdf(pdf, report_data)
        elif report_type == 'empty_hours':
            self._generate_empty_hours_pdf(pdf, report_data)

        # Generar gráfico y añadirlo al PDF
        img_data = _generate_report_chart(report_data, report_type)
        if img_data:
            temp_img = "temp_chart.png"
            with open(temp_img, "wb") as f:
                f.write(img_data)

            pdf.image(temp_img, x=10, y=pdf.get_y(), w=180)
            os.remove(temp_img)

        return pdf.output(dest='S').encode('latin1')

    # =============================================
    # MÉTODOS PRIVADOS
    # =============================================

    def _get_work_schedule(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene el horario de trabajo configurado.

        Returns:
            dict: Horario de trabajo por día
        """
        query = "SELECT * FROM work_schedule"
        schedule_data = self.db_manager.execute_query(query, fetch_all=True)

        schedule = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day_num, day in enumerate(days):
            day_schedule = next((item for item in schedule_data if item['day_of_week'] == day_num), None)

            if day_schedule:
                schedule[day] = {
                    'start_time': day_schedule['start_time'],
                    'end_time': day_schedule['end_time'],
                    'is_working_day': bool(day_schedule['is_working_day'])
                }
            else:
                schedule[day] = {
                    'start_time': '09:00',
                    'end_time': '17:00',
                    'is_working_day': day_num < 5  # Lunes a viernes por defecto
                }

        return schedule

    def _get_appointments_in_range(
            self,
            start_date: str,
            end_date: str
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Obtiene las citas agendadas en el rango de fechas.

        Args:
            start_date (str): Fecha de inicio en formato YYYY-MM-DD
            end_date (str): Fecha de fin en formato YYYY-MM-DD

        Returns:
            dict: Citas agrupadas por fecha
        """
        query = """
                SELECT
                    date, start_time, end_time
                FROM
                    appointments
                WHERE
                    date BETWEEN ? \
                  AND ?
                  AND status != 'cancelled'
                ORDER BY
                    date, start_time \
                """

        appointments = self.db_manager.execute_query(
            query,
            (start_date, end_date),
            fetch_all=True
        )

        grouped = {}
        for appt in appointments:
            date_str = appt['date']
            if date_str not in grouped:
                grouped[date_str] = []

            grouped[date_str].append({
                'start_time': appt['start_time'],
                'end_time': appt['end_time']
            })

        return grouped

    def _generate_worked_hours_pdf(self, pdf: FPDF, report_data: Dict[str, Any]):
        """Genera la sección de horas trabajadas para el PDF."""
        pass  # Implementar según necesidad


    def _generate_empty_hours_pdf(self, pdf: FPDF, report_data: Dict[str, Any]):
        """Genera la sección de horas vacías para el PDF."""
        pass  # Implementar según necesidad