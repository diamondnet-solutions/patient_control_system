# =============================================
# HEADER INFORMATION
# =============================================
# Nombre del archivo: appointment_manager.py
# Propósito: Gestión integral de citas médicas (creación, modificación, cancelación)
# Empresa: DiamondNetSolutions
# Autor: [Nombre del Autor]
# Fecha de creación: [Fecha de Creación]
# Última modificación: [Fecha de Modificación]
# =============================================

"""
Módulo para la gestión de citas en el sistema de control de pacientes.
Permite crear, modificar, consultar y cancelar citas.
"""

# =============================================
# LIBRERÍAS
# =============================================
# Librerías estándar de Python
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

# Librerías de terceros
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Librerías propias del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import DatabaseManager


class AppointmentManager:
    """
    Clase para gestionar las citas médicas en el sistema.

    Proporciona funcionalidades para:
    - Crear, modificar y cancelar citas
    - Consultar disponibilidad de horarios
    - Enviar notificaciones por correo electrónico
    - Generar reportes de citas
    """

    def __init__(self, db_manager: DatabaseManager = None):
        """
        Inicializa el gestor de citas.

        Args:
            db_manager (DatabaseManager): Instancia de DatabaseManager (opcional)
        """
        self.db_manager = db_manager or DatabaseManager()
        self.email_settings = self._load_email_settings()

    def _load_email_settings(self) -> Dict[str, Any]:
        """
        Carga la configuración de email desde la base de datos.

        Returns:
            dict: Configuración del servidor SMTP
        """
        try:
            settings = self.db_manager.get_table_data('email_settings', limit=1)
            if settings:
                return {
                    'smtp_server': settings[0]['smtp_server'],
                    'smtp_port': settings[0]['smtp_port'],
                    'email': settings[0]['username'],
                    'password': settings[0]['password'],
                    'sender_email': settings[0]['sender_email'],
                    'sender_name': settings[0]['sender_name']
                }
            return {}
        except Exception as e:
            print(f"Error al cargar configuración de email: {e}")
            return {}

    def create_appointment(
            self,
            patient_id: int,
            date: str,
            start_time: str,
            end_time: str,
            doctor: str,
            reason: str,
            status: str = "scheduled"
    ) -> Optional[int]:
        """
        Crea una nueva cita en la base de datos.

        Args:
            patient_id (int): ID del paciente
            date (str): Fecha de la cita (YYYY-MM-DD)
            start_time (str): Hora de inicio (HH:MM)
            end_time (str): Hora de fin (HH:MM)
            doctor (str): Nombre del doctor
            reason (str): Motivo de la cita
            status (str): Estado de la cita (default: "scheduled")

        Returns:
            int: ID de la cita creada o None si hubo error
        """
        try:
            # Verificar disponibilidad
            if not self.is_time_available(date, start_time, end_time):
                raise ValueError("El horario seleccionado no está disponible")

            # Calcular duración en minutos
            start_dt = datetime.strptime(start_time, '%H:%M')
            end_dt = datetime.strptime(end_time, '%H:%M')
            duration = int((end_dt - start_dt).total_seconds() / 60)

            # Crear la cita
            appointment_data = {
                'patient_id': patient_id,
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'status': status,
                'notes': reason
            }

            appointment_id = self.db_manager.insert_record('appointments', appointment_data)

            # Obtener información del paciente para el correo
            patient_info = self._get_patient_info(patient_id)
            if patient_info and patient_info.get('email'):
                self._send_appointment_email(
                    patient_info['email'],
                    f"{patient_info['first_name']} {patient_info['last_name']}",
                    date,
                    start_time,
                    doctor,
                    reason,
                    appointment_id,
                    'created'
                )

            return appointment_id

        except sqlite3.Error as e:
            print(f"Error al crear la cita: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None

    def update_appointment(
            self,
            appointment_id: int,
            **kwargs: Dict[str, Any]
    ) -> bool:
        """
        Actualiza los datos de una cita existente.

        Args:
            appointment_id (int): ID de la cita a actualizar
            **kwargs: Campos a actualizar (date, start_time, end_time, status, notes)

        Returns:
            bool: True si la actualización fue exitosa
        """
        try:
            # Verificar que la cita existe
            appointment = self.get_appointment(appointment_id)
            if not appointment:
                raise ValueError(f"No existe cita con ID {appointment_id}")

            # Verificar disponibilidad si se cambia fecha/hora
            if 'date' in kwargs or 'start_time' in kwargs or 'end_time' in kwargs:
                date = kwargs.get('date', appointment['date'])
                start_time = kwargs.get('start_time', appointment['start_time'])
                end_time = kwargs.get('end_time', appointment['end_time'])

                if not self.is_time_available(date, start_time, end_time, exclude_id=appointment_id):
                    raise ValueError("El nuevo horario no está disponible")

            # Actualizar la cita
            return self.db_manager.update_record('appointments', appointment_id, kwargs)

        except sqlite3.Error as e:
            print(f"Error al actualizar la cita: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False

    def cancel_appointment(
            self,
            appointment_id: int,
            reason: str = "Cancelada por el paciente"
    ) -> bool:
        """
        Cancela una cita existente.

        Args:
            appointment_id (int): ID de la cita a cancelar
            reason (str): Motivo de la cancelación

        Returns:
            bool: True si la cancelación fue exitosa
        """
        try:
            # Obtener datos de la cita antes de cancelarla
            appointment = self.get_appointment(appointment_id)
            if not appointment:
                raise ValueError(f"No existe cita con ID {appointment_id}")

            # Actualizar estado y motivo
            update_data = {
                'status': 'cancelled',
                'notes': f"{appointment.get('notes', '')}\nMotivo cancelación: {reason}"
            }

            success = self.db_manager.update_record('appointments', appointment_id, update_data)

            # Notificar al paciente si la actualización fue exitosa
            if success and appointment.get('patient_id'):
                patient_info = self._get_patient_info(appointment['patient_id'])
                if patient_info and patient_info.get('email'):
                    self._send_appointment_email(
                        patient_info['email'],
                        f"{patient_info['first_name']} {patient_info['last_name']}",
                        appointment['date'],
                        appointment['start_time'],
                        "",
                        appointment.get('notes', ''),
                        appointment_id,
                        'cancelled',
                        cancellation_reason=reason
                    )

            return success

        except sqlite3.Error as e:
            print(f"Error al cancelar la cita: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False

    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de una cita específica.

        Args:
            appointment_id (int): ID de la cita

        Returns:
            dict: Datos de la cita o None si no existe
        """
        query = """
                SELECT a.*,
                       p.first_name,
                       p.last_name,
                       p.email,
                       p.phone
                FROM appointments a
                         JOIN patients p ON a.patient_id = p.id
                WHERE a.id = ?
                """
        return self.db_manager.execute_query(query, (appointment_id,), fetch_one=True)

    def get_patient_appointments(
            self,
            patient_id: int,
            include_past: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las citas de un paciente.

        Args:
            patient_id (int): ID del paciente
            include_past (bool): Incluir citas pasadas (default: True)

        Returns:
            list: Lista de citas del paciente
        """
        query = """
                SELECT a.*
                FROM appointments a
                WHERE a.patient_id = ?
                """

        if not include_past:
            today = datetime.now().strftime('%Y-%m-%d')
            query += f" AND (a.date > '{today}' OR (a.date = '{today}' AND a.start_time >= time('now', 'localtime')))"

        query += " ORDER BY a.date, a.start_time"

        return self.db_manager.execute_query(query, (patient_id,), fetch_all=True)

    def get_daily_appointments(self, date: str) -> List[Dict[str, Any]]:
        """
        Obtiene todas las citas para un día específico.

        Args:
            date (str): Fecha en formato YYYY-MM-DD

        Returns:
            list: Citas del día ordenadas por hora
        """
        query = """
                SELECT a.*,
                       p.first_name,
                       p.last_name
                FROM appointments a
                         JOIN patients p ON a.patient_id = p.id
                WHERE a.date = ?
                ORDER BY a.start_time
                """
        return self.db_manager.execute_query(query, (date,), fetch_all=True)

    def is_time_available(
            self,
            date: str,
            start_time: str,
            end_time: str,
            exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si un horario está disponible.

        Args:
            date (str): Fecha (YYYY-MM-DD)
            start_time (str): Hora inicio (HH:MM)
            end_time (str): Hora fin (HH:MM)
            exclude_id (int): ID de cita a excluir (para actualizaciones)

        Returns:
            bool: True si el horario está disponible
        """
        query = """
                SELECT id
                FROM appointments
                WHERE date = ?
                  AND status != 'cancelled'
                  AND (
                    (start_time \
                    < ? \
                  AND end_time \
                    > ?)
                   OR
                    (start_time \
                    < ? \
                  AND end_time \
                    > ?)
                   OR
                    (start_time >= ? \
                  AND end_time <= ?)
                    )
                """

        if exclude_id:
            query += " AND id != ?"
            params = (
                date, end_time, start_time,
                start_time, end_time,
                start_time, end_time,
                exclude_id
            )
        else:
            params = (
                date, end_time, start_time,
                start_time, end_time,
                start_time, end_time
            )

        result = self.db_manager.execute_query(query, params, fetch_all=True)
        return len(result) == 0

    def _get_patient_info(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información básica del paciente.

        Args:
            patient_id (int): ID del paciente

        Returns:
            dict: Información del paciente o None
        """
        query = """
                SELECT first_name, last_name, email, phone
                FROM patients
                WHERE id = ?
                """
        return self.db_manager.execute_query(query, (patient_id,), fetch_one=True)

    def _send_appointment_email(
            self,
            email: str,
            patient_name: str,
            date: str,
            time: str,
            doctor: str,
            reason: str,
            appointment_id: int,
            action_type: str,
            cancellation_reason: Optional[str] = None
    ) -> None:
        """
        Envía un correo electrónico sobre la cita.

        Args:
            email (str): Correo del paciente
            patient_name (str): Nombre completo
            date (str): Fecha cita
            time (str): Hora cita
            doctor (str): Nombre doctor
            reason (str): Motivo cita
            appointment_id (int): ID cita
            action_type (str): Tipo de acción (created/updated/cancelled)
            cancellation_reason (str): Motivo cancelación (opcional)
        """
        if not self.email_settings:
            print("Configuración de email no disponible")
            return

        try:
            # Crear mensaje según tipo de acción
            subject_map = {
                'created': 'Confirmación de cita médica',
                'updated': 'Actualización de cita médica',
                'cancelled': 'Cancelación de cita médica'
            }
            subject = subject_map.get(action_type, 'Notificación de cita médica')

            # Formatear fecha
            formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')

            # Construir cuerpo del mensaje
            body = f"""
            <html>
            <body>
            <h2>{subject}</h2>
            <p>Estimado/a {patient_name},</p>
            """

            if action_type == 'cancelled':
                body += f"""
                <p>Su cita ha sido cancelada con los siguientes detalles:</p>
                <ul>
                    <li><strong>Fecha:</strong> {formatted_date}</li>
                    <li><strong>Hora:</strong> {time}</li>
                    <li><strong>Motivo cancelación:</strong> {cancellation_reason or 'No especificado'}</li>
                </ul>
                """
            else:
                body += f"""
                <p>Su cita ha sido {action_type} con los siguientes detalles:</p>
                <ul>
                    <li><strong>Fecha:</strong> {formatted_date}</li>
                    <li><strong>Hora:</strong> {time}</li>
                    <li><strong>Doctor:</strong> {doctor}</li>
                    <li><strong>Motivo:</strong> {reason}</li>
                </ul>
                """

            body += """
            <p>Atentamente,<br>El equipo médico</p>
            </body>
            </html>
            """

            # Configurar mensaje de email
            msg = MIMEMultipart()
            msg['From'] = self.email_settings['sender_email']
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            # Enviar email (comentar en desarrollo)
            """
            with smtplib.SMTP(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                server.starttls()
                server.login(self.email_settings['email'], self.email_settings['password'])
                server.send_message(msg)
            """
            print(f"Simulando envío de email a {email}")

        except Exception as e:
            print(f"Error al enviar email: {e}")

    def get_filtered_appointments(self, date=None, patient_id=None, status=None):
        """Obtiene citas filtradas por fecha, paciente o estado"""
        query = """
                SELECT a.*, p.first_name as patient_first_name, p.last_name as patient_last_name
                FROM appointments a
                         JOIN patients p ON a.patient_id = p.id
                WHERE 1 = 1 \
                """
        params = []

        if date:
            query += " AND a.date = ?"
            params.append(date)
        if patient_id:
            query += " AND a.patient_id = ?"
            params.append(patient_id)
        if status:
            query += " AND a.status = ?"
            params.append(status)

        query += " ORDER BY a.date, a.start_time"

        return self.db_manager.execute_query(query, params, fetch_all=True)

    def update_appointment_status(self, appointment_id, status):
        """Actualiza el estado de una cita"""
        query = "UPDATE appointments SET status = ? WHERE id = ?"
        return self.db_manager.execute_query(query, (status, appointment_id))

    def get_appointment_by_id(self, appointment_id):
        """Obtiene una cita por su ID"""
        query = """
                SELECT a.*, p.first_name, p.last_name, p.email
                FROM appointments a
                         JOIN patients p ON a.patient_id = p.id
                WHERE a.id = ? \
                """
        return self.db_manager.execute_query(query, (appointment_id,), fetch_one=True)

    def get_available_time_slots(
            self,
            date: str,
            duration: int = 30,
            start_hour: int = 9,
            end_hour: int = 18
    ) -> List[str]:
        """
        Obtiene horarios disponibles para agendar citas.

        Args:
            date (str): Fecha (YYYY-MM-DD)
            duration (int): Duración en minutos (default: 30)
            start_hour (int): Hora inicio (default: 9)
            end_hour (int): Hora fin (default: 18)

        Returns:
            list: Lista de horarios disponibles (HH:MM)
        """
        try:
            # Obtener citas existentes para la fecha
            appointments = self.get_daily_appointments(date)
            booked_slots = []

            # Calcular slots ocupados
            for appt in appointments:
                if appt['status'] == 'cancelled':
                    continue

                start = datetime.strptime(appt['start_time'], '%H:%M')
                end = datetime.strptime(appt['end_time'], '%H:%M')

                current = start
                while current < end:
                    booked_slots.append(current.strftime('%H:%M'))
                    current += timedelta(minutes=15)

            # Generar todos los posibles slots
            all_slots = []
            for hour in range(start_hour, end_hour):
                for minute in [0, 15, 30, 45]:
                    slot_time = datetime(2020, 1, 1, hour, minute)
                    all_slots.append(slot_time.strftime('%H:%M'))

            # Filtrar slots disponibles
            available_slots = []
            slot_duration = timedelta(minutes=duration)

            for slot in all_slots:
                slot_time = datetime.strptime(slot, '%H:%M')
                end_time = slot_time + slot_duration

                # Verificar si el slot está completamente disponible
                current = slot_time
                is_available = True

                while current < end_time:
                    if current.strftime('%H:%M') in booked_slots:
                        is_available = False
                        break
                    current += timedelta(minutes=15)

                if is_available and end_time <= datetime(2020, 1, 1, end_hour, 0):
                    available_slots.append(slot)

            return available_slots

        except Exception as e:
            print(f"Error al calcular slots disponibles: {e}")
            return []