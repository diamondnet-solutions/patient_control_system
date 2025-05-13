#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo mejorado para el manejo de correos electrónicos con seguimiento avanzado
"""

import os
import smtplib
import logging
import uuid
import json

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from string import Template
from datetime import datetime
import sqlite3

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('email_handler')


class EmailConfig:
    """Clase para manejar la configuración de correo electrónico"""

    def __init__(self, config_path=None):
        """
        Inicializa la configuración de correo

        Args:
            config_path (str, optional): Ruta al archivo de configuración de correo
        """
        self.config_path = config_path  # Asegúrate de asignar esto primero

        # Si no se proporciona una ruta específica, usar la predeterminada
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_path = os.path.join(base_dir, 'data', 'email_config.json')

        # Cargar la configuración
        self.config = self._load_config()  # Luego cargar la configuración

    def _load_config(self):
        """
        Carga la configuración desde el archivo JSON

        Returns:
            dict: Configuración de correo electrónico
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                # Crear configuración por defecto
                default_config = {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "smtp_username": "",
                    "smtp_password": "",
                    "sender_name": "Sistema Clínico",
                    "sender_email": "",
                    "use_tls": True,
                    "templates_path": "templates/email"
                }

                # Crear directorio si no existe
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

                # Guardar configuración por defecto
                with open(self.config_path, 'w', encoding='utf-8') as file:
                    json.dump(default_config, file, indent=4)

                return default_config
        except Exception as e:
            logger.error(f"Error al cargar configuración de correo: {e}")
            # Devolver configuración mínima
            return {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "sender_email": "",
                "use_tls": True
            }

    def save_config(self, config_data):
        """
        Guarda la configuración en el archivo JSON

        Args:
            config_data (dict): Datos de configuración a guardar

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            # Guardar configuración
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, indent=4)

            # Actualizar configuración en memoria
            self.config = config_data
            logger.info("Configuración de correo guardada correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al guardar configuración de correo: {e}")
            return False

    def get_config(self):
        """
        Obtiene la configuración actual

        Returns:
            dict: Configuración de correo electrónico
        """
        return self.config

    def is_configured(self):
        """
        Verifica si el correo está configurado

        Returns:
            bool: True si está configurado, False en caso contrario
        """
        return (
                self.config.get("smtp_username") and
                self.config.get("smtp_password") and
                self.config.get("sender_email")
        )


class EmailTracker:
    """Clase para rastrear correos enviados y recibir confirmaciones"""

    def __init__(self, db_path=None):
        """
        Inicializa el rastreador de correos

        Args:
            db_path (str, optional): Ruta al archivo de la base de datos
        """
        # Si no se proporciona una ruta específica, usar la predeterminada
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, 'data', 'clinic.db')
        else:
            self.db_path = db_path

        # Crear tabla si no existe
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        """Crea la tabla para rastrear correos si no existe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tracking_id TEXT UNIQUE NOT NULL,
                    appointment_id INTEGER,
                    email_type TEXT,
                    recipient_email TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    sent_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'sent',
                    delivery_status TEXT,
                    open_count INTEGER DEFAULT 0,
                    last_open_date TEXT,
                    response_content TEXT,
                    response_date TEXT,
                    error_message TEXT,
                    metadata TEXT,
                    FOREIGN KEY (appointment_id) REFERENCES appointments (id)
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("Tabla de seguimiento de correos creada/verificada correctamente")
        except sqlite3.Error as e:
            logger.error(f"Error al crear tabla de seguimiento de correos: {e}")

    def register_email(self, recipient_email, subject, email_type=None, appointment_id=None, metadata=None):
        """
        Registra un correo en la base de datos con la nueva estructura

        Args:
            recipient_email: Email del destinatario
            subject: Asunto del email
            email_type: Tipo de email (confirmación, recordatorio, etc.)
            appointment_id: ID de cita relacionada
            metadata: Diccionario con metadatos adicionales

        Returns:
            str: tracking_id o None si falla
        """
        try:
            tracking_id = str(uuid.uuid4())
            metadata_json = json.dumps(metadata) if metadata else None

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           INSERT INTO email_tracking (
                               tracking_id, 
                               appointment_id, 
                               email_type,                 
                               recipient_email, 
                               subject, 
                               metadata)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', (tracking_id, appointment_id, email_type,
                                 recipient_email, subject, metadata_json))

            conn.commit()
            conn.close()

            logger.info(f"Correo registrado con ID: {tracking_id}")
            return tracking_id
        except sqlite3.Error as e:
            logger.error(f"Error al registrar correo: {e}")
            return None

    def update_email_status(self, tracking_id, status, delivery_status=None, error_message=None):
        """
        Actualiza el estado de un correo enviado

        Args:
            tracking_id: ID de seguimiento
            status: Nuevo estado (sent, delivered, opened, etc.)
            delivery_status: Estado de entrega del proveedor SMTP
            error_message: Mensaje de error si falló

        Returns:
            bool: True si éxito, False si falla
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if error_message:
                cursor.execute('''
                               UPDATE email_tracking
                               SET status          = ?,
                                   delivery_status = ?,
                                   error_message   = ?
                               WHERE tracking_id = ?
                               ''', (status, delivery_status, error_message, tracking_id))
            else:
                cursor.execute('''
                               UPDATE email_tracking
                               SET status          = ?,
                                   delivery_status = ?
                               WHERE tracking_id = ?
                               ''', (status, delivery_status, tracking_id))

            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al actualizar estado: {e}")
            return False

    def record_email_open(self, tracking_id):
        """Registra que un email fue abierto"""
        try:
            current_date = datetime.now().isoformat()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           UPDATE email_tracking
                           SET open_count     = open_count + 1,
                               last_open_date = ?,
                               status         = 'opened'
                           WHERE tracking_id = ?
                           ''', (current_date, tracking_id))

            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al registrar apertura: {e}")
            return False

    def get_email_by_tracking_id(self, tracking_id):
        """
        Obtiene información de un correo por su ID de seguimiento

        Args:
            tracking_id (str): ID de seguimiento del correo

        Returns:
            dict: Información del correo o None si no se encuentra
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM email_tracking WHERE tracking_id = ?', (tracking_id,))
            result = cursor.fetchone()

            conn.close()

            if result:
                return dict(result)
            else:
                return None
        except sqlite3.Error as e:
            logger.error(f"Error al obtener información del correo: {e}")
            return None

    def get_emails_by_appointment(self, appointment_id):
        """
        Obtiene todos los correos relacionados con una cita

        Args:
            appointment_id (int): ID de la cita

        Returns:
            list: Lista de correos relacionados con la cita
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM email_tracking WHERE appointment_id = ? ORDER BY sent_date DESC',
                           (appointment_id,))
            results = cursor.fetchall()

            conn.close()

            return [dict(row) for row in results]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener correos por cita: {e}")
            return []


class EmailSender:
    """Clase para enviar correos electrónicos con el nuevo sistema de tracking"""

    def __init__(self, config_path=None):
        """
        Inicializa el emisor de correos

        Args:
            config_path (str, optional): Ruta al archivo de configuración
        """
        self.email_config = EmailConfig(config_path)
        self.email_tracker = EmailTracker()

    def send_email(self, recipient_email, subject, body_text, body_html=None,
                  attachments=None, email_type=None, appointment_id=None, metadata=None):
        """
        Envía un correo electrónico

        Args:
            recipient_email (str): Correo electrónico del destinatario
            subject (str): Asunto del correo
            body_text (str): Cuerpo del mensaje en texto plano
            body_html (str, optional): Cuerpo del mensaje en HTML
            attachments (list, optional): Lista de rutas de archivos adjuntos
            appointment_id (int, optional): ID de la cita relacionada

        Returns:
            str: ID de seguimiento del correo o None si falla
        """
        if not self.email_config.is_configured():
            logger.error("Configuración de correo no completada")
            return None

        config = self.email_config.get_config()

        # Registrar el email antes de enviarlo
        tracking_id = self.email_tracker.register_email(
            recipient_email=recipient_email,
            subject=subject,
            email_type=email_type,
            appointment_id=appointment_id,
            metadata=metadata
        )

        if not tracking_id:
            logger.error("No se pudo registrar el correo para tracking")
            return None

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{config.get('sender_name', 'Sistema')} <{config['sender_email']}>"
            msg['To'] = recipient_email

            # Añadir headers para tracking
            msg['X-Tracking-ID'] = tracking_id
            if appointment_id:
                msg['X-Appointment-ID'] = str(appointment_id)

            # Partes del mensaje (texto y HTML)
            msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
            if body_html:
                msg.attach(MIMEText(body_html, 'html', 'utf-8'))

            # Adjuntos
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                        msg.attach(part)

            # Envío SMTP
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.ehlo()
                if config.get('use_tls', True):
                    server.starttls()
                    server.ehlo()
                server.login(config['smtp_username'], config['smtp_password'])
                server.send_message(msg)

            # Actualizar estado a delivered
            self.email_tracker.update_email_status(
                tracking_id=tracking_id,
                status='delivered',
                delivery_status='sent_to_provider'
            )

            logger.info(f"Email enviado a {recipient_email} (ID: {tracking_id})")
            return tracking_id

        except smtplib.SMTPException as e:
            logger.error(f"Error SMTP al enviar email: {e}")
            self.email_tracker.update_email_status(
                tracking_id=tracking_id,
                status='failed',
                error_message=str(e)
            )
            return None

        except Exception as e:
            logger.error(f"Error inesperado al enviar email: {e}")
            self.email_tracker.update_email_status(
                tracking_id=tracking_id,
                status='failed',
                error_message=str(e)
            )
            return None

    def send_template_email(self, recipient_email, subject, template_name,
                            template_data, appointment_id=None, attachments=None):
        """
        Envía un correo electrónico basado en una plantilla

        Args:
            recipient_email (str): Correo electrónico del destinatario
            subject (str): Asunto del correo
            template_name (str): Nombre de la plantilla (sin extensión)
            template_data (dict): Datos para rellenar la plantilla
            appointment_id (int, optional): ID de la cita relacionada
            attachments (list, optional): Lista de rutas de archivos adjuntos

        Returns:
            str: ID de seguimiento del correo o None si falla
        """
        try:
            config = self.email_config.get_config()
            templates_path = config.get('templates_path', 'templates/email')

            # Obtener rutas de plantillas
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            text_template_path = os.path.join(base_dir, templates_path, f"{template_name}.txt")
            html_template_path = os.path.join(base_dir, templates_path, f"{template_name}.html")

            # Cargar y procesar plantilla de texto
            body_text = None
            if os.path.exists(text_template_path):
                with open(text_template_path, 'r', encoding='utf-8') as f:
                    template_text = Template(f.read())
                body_text = template_text.safe_substitute(template_data)
            else:
                # Si no hay plantilla, generar texto plano básico
                body_text = "Este es un mensaje automático del Sistema Clínico.\n\n"
                for key, value in template_data.items():
                    body_text += f"{key}: {value}\n"

            # Cargar y procesar plantilla HTML
            body_html = None
            if os.path.exists(html_template_path):
                with open(html_template_path, 'r', encoding='utf-8') as f:
                    template_html = Template(f.read())
                body_html = template_html.safe_substitute(template_data)

            # Enviar correo
            return self.send_email(recipient_email, subject, body_text, body_html,
                                   attachments, appointment_id)

        except Exception as e:
            logger.error(f"Error al enviar correo con plantilla: {e}")
            return None


def send_appointment_email(recipient_email, subject, body, appointment_id=None):
    """
    Función de utilidad para enviar correo relacionado con una cita

    Args:
        recipient_email (str): Correo electrónico del destinatario
        subject (str): Asunto del correo
        body (str): Cuerpo del mensaje
        appointment_id (int, optional): ID de la cita relacionada

    Returns:
        str: ID de seguimiento del correo o None si falla
    """
    sender = EmailSender()
    return sender.send_email(recipient_email, subject, body, appointment_id=appointment_id)


def send_appointment_confirmation(recipient_email, appointment_data, patient_data):
    """
    Envía un correo de confirmación de cita

    Args:
        recipient_email (str): Correo electrónico del destinatario
        appointment_data (dict): Datos de la cita
        patient_data (dict): Datos del paciente

    Returns:
        str: ID de seguimiento del correo o None si falla
    """
    sender = EmailSender()

    subject = f"Confirmación de Cita - {appointment_data['date']}"

    # Preparar datos para la plantilla
    template_data = {
        'patient_name': f"{patient_data['first_name']} {patient_data['last_name']}",
        'appointment_date': appointment_data['date'],
        'appointment_time': f"{appointment_data['start_time']} - {appointment_data['end_time']}",
        'doctor_name': appointment_data.get('doctor_name', 'Su médico'),
        'clinic_name': 'Nuestra Clínica',
        'clinic_address': 'Dirección de la Clínica',
        'clinic_phone': 'Teléfono de la Clínica',
        'notes': appointment_data.get('notes', 'Sin notas adicionales')
    }

    # Enviar usando plantilla
    return sender.send_template_email(
        recipient_email,
        subject,
        'appointment_confirmation',
        template_data,
        appointment_data['id']
    )


def send_appointment_reminder(recipient_email, appointment_data, patient_data, days_before=1):
    """
    Envía un recordatorio de cita

    Args:
        recipient_email (str): Correo electrónico del destinatario
        appointment_data (dict): Datos de la cita
        patient_data (dict): Datos del paciente
        days_before (int): Días antes de la cita para enviar el recordatorio

    Returns:
        str: ID de seguimiento del correo o None si falla
    """
    sender = EmailSender()

    subject = f"Recordatorio de Cita - {appointment_data['date']}"

    # Preparar datos para la plantilla
    template_data = {
        'patient_name': f"{patient_data['first_name']} {patient_data['last_name']}",
        'appointment_date': appointment_data['date'],
        'appointment_time': f"{appointment_data['start_time']} - {appointment_data['end_time']}",
        'doctor_name': appointment_data.get('doctor_name', 'Su médico'),
        'clinic_name': 'Nuestra Clínica',
        'clinic_address': 'Dirección de la Clínica',
        'clinic_phone': 'Teléfono de la Clínica',
        'days_before': days_before,
        'notes': appointment_data.get('notes', 'Sin notas adicionales')
    }

    # Enviar usando plantilla
    return sender.send_template_email(
        recipient_email,
        subject,
        'appointment_reminder',
        template_data,
        appointment_data['id']
    )


def send_appointment_cancellation(recipient_email, appointment_data, patient_data, reason=None):
    """
    Envía un correo de cancelación de cita

    Args:
        recipient_email (str): Correo electrónico del destinatario
        appointment_data (dict): Datos de la cita
        patient_data (dict): Datos del paciente
        reason (str, optional): Motivo de la cancelación

    Returns:
        str: ID de seguimiento del correo o None si falla
    """
    sender = EmailSender()

    subject = f"Cancelación de Cita - {appointment_data['date']}"

    # Preparar datos para la plantilla
    template_data = {
        'patient_name': f"{patient_data['first_name']} {patient_data['last_name']}",
        'appointment_date': appointment_data['date'],
        'appointment_time': f"{appointment_data['start_time']} - {appointment_data['end_time']}",
        'doctor_name': appointment_data.get('doctor_name', 'Su médico'),
        'clinic_name': 'Nuestra Clínica',
        'clinic_phone': 'Teléfono de la Clínica',
        'reason': reason if reason else 'No se ha especificado un motivo'
    }

    # Enviar usando plantilla
    return sender.send_template_email(
        recipient_email,
        subject,
        'appointment_cancellation',
        template_data,
        appointment_data['id']
    )


def send_test_email(recipient_email):
    """
    Envía un correo de prueba para verificar la configuración

    Args:
        recipient_email (str): Correo electrónico del destinatario

    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    sender = EmailSender()
    subject = "Prueba de configuración de correo"
    body = """
    Este es un correo de prueba para verificar la configuración de correo del Sistema Clínico.

    Si recibe este mensaje, la configuración de correo funciona correctamente.

    Saludos,
    Sistema Clínico
    """

    tracking_id = sender.send_email(recipient_email, subject, body)
    return tracking_id is not None
