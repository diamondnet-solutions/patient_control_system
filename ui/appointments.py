# =============================================
# Nombre del archivo: appointment.py
# Propósito: Gestión integral de citas médicas con interfaz a
# Empresa: DiamondNetSolutions
# Autor original: Eliazar
# Modificado por: Claude
# Fecha de modificación: 17/05/2025
# =============================================

import re
from datetime import datetime

import customtkinter as ctk
import tkinter as tk
from tkcalendar import Calendar, DateEntry
from CTkMessagebox import CTkMessagebox

from core.appointment_manager import AppointmentManager
from core.patient_manager import PatientManager
from core.treatment_manager import TreatmentManager
from utils.email_handler import send_appointment_email

# Configuración de tema de CustomTkinter
ctk.set_appearance_mode("light")  # Modos: system (default), light, dark
ctk.set_default_color_theme("blue")  # Temas: blue (default), dark-blue, green

class AppointmentsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Variables de clase
        self.colors = None
        self.selection_label = None
        self.search_button = None
        self.search_button = None
        self.action_frame = None
        self.insurance_combo = None
        self.insurance_var = None
        self.status_combo = None
        self.status_var = None
        self.patient_var = None
        self.patient_combo = None
        self.date_entry = None
        self.calendar = None
        self.right_panel = None
        self.left_panel = None
        self.top_frame = None
        self.new_button = None
        self.header_frame = None
        self.appointments_container = None
        self.selected_appointments = set()
        self.appointment_cards = {}
        self.filter_values = {
            "date": None,
            "patient_id": None,
            "status": None,
            "insurance_type": None
        }

        # Inicializar managers
        self.appointment_manager = AppointmentManager()
        self.patient_manager = PatientManager()
        self.treatment_manager = TreatmentManager()

        # Configurar colores
        self.configure(fg_color="#F5F7FA")

        # Configurar interfaz
        self.pack(fill="both", expand=True)
        self.setup_ui()

        # Cargar datos iniciales
        self.load_appointments_table()

    def setup_ui(self):
        """Configurar la interfaz de usuario para la gestión de citas"""
        # Marco de encabezado
        self.header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", height=60)
        self.header_frame.pack(fill="x", padx=0, pady=(0, 10))

        # Título
        title_label = ctk.CTkLabel(
            self.header_frame,
            text="Citas Médicas",
            font=("Roboto", 22, "bold")
        )
        title_label.pack(side="left", padx=20, pady=10)

        # Botón de nueva cita
        self.new_button = ctk.CTkButton(
            self.header_frame,
            text="+ Nueva Cita",
            font=("Roboto", 14),
            fg_color="#28C7A2",
            hover_color="#1DAA8B",
            corner_radius=8,
            command=self.new_appointment
        )
        self.new_button.pack(side="right", padx=20, pady=10)

        # Marco para filtros y calendario
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Dividir en dos paneles
        self.left_panel = ctk.CTkFrame(self.top_frame, fg_color="#FFFFFF", corner_radius=10)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10), expand=False)

        self.right_panel = ctk.CTkFrame(self.top_frame, fg_color="#FFFFFF", corner_radius=10)
        self.right_panel.pack(side="right", fill="both", expand=True)

        # Panel izquierdo: Calendario
        calendar_label = ctk.CTkLabel(
            self.left_panel,
            text="Calendario",
            font=("Roboto", 16, "bold")
        )
        calendar_label.pack(padx=15, pady=(15, 5), anchor="w")

        # Contenedor para el calendario tradicional
        calendar_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        calendar_container.pack(padx=15, pady=10, fill="both", expand=True)

        # Usar tkcalendar en un contenedor
        self.calendar = Calendar(
            calendar_container,
            selectmode='day',
            locale='es_ES',
            date_pattern='dd/mm/yyyy',
            background="#FFFFFF",
            foreground="#000000",
            headersbackground="#6774BD",
            headersforeground="#FFFFFF",
            selectbackground="#28C7A2",
            selectforeground="#FFFFFF",
            normalbackground="#FFFFFF",
            normalforeground="#000000",
            weekendbackground="#F0F1FA",
            weekendforeground="#000000",
        )
        self.calendar.pack(padx=5, pady=5, fill="both", expand=True)
        self.calendar.bind("<<CalendarSelected>>", self.on_date_selected)

        # Panel derecho: Filtros
        filter_label = ctk.CTkLabel(
            self.right_panel,
            text="Filtros",
            font=("Roboto", 16, "bold")
        )
        filter_label.pack(padx=15, pady=(15, 5), anchor="w")

        # Marco para filtros
        filters_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        filters_frame.pack(padx=15, pady=5, fill="x")

        # Control de fecha
        date_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=5)

        date_label = ctk.CTkLabel(date_frame, text="Fecha:", width=80)
        date_label.pack(side="left", padx=(0, 10))

        date_container = ctk.CTkFrame(date_frame, fg_color="transparent", height=30)
        date_container.pack(side="left", fill="x", expand=True)

        # DateEntry colocado en el contenedor
        self.date_entry = DateEntry(
            date_container,
            width=12,
            background='#6774BD',
            foreground='white',
            borderwidth=0,
            date_pattern='dd/mm/yyyy'
        )
        self.date_entry.pack(fill="both", expand=True)
        self.date_entry.bind("<<DateEntrySelected>>", self.on_date_entry_selected)

        # Filtro por paciente
        patient_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        patient_frame.pack(fill="x", pady=5)

        patient_label = ctk.CTkLabel(patient_frame, text="Paciente:", width=80)
        patient_label.pack(side="left", padx=(0, 10))

        self.patient_var = ctk.StringVar(value="Todos")
        self.patient_combo = ctk.CTkComboBox(
            patient_frame,
            variable=self.patient_var,
            width=200,
            values=["Cargando..."],
            dropdown_fg_color="#FFFFFF",
            button_color="#6774BD",
            button_hover_color="#5363BD"
        )
        self.patient_combo.pack(side="left", fill="x", expand=True)

        # Filtro por estado
        status_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=5)

        status_label = ctk.CTkLabel(status_frame, text="Estado:", width=80)
        status_label.pack(side="left", padx=(0, 10))

        self.status_var = ctk.StringVar(value="Todos")
        self.status_combo = ctk.CTkComboBox(
            status_frame,
            variable=self.status_var,
            values=["Todos", "Programada", "Confirmada", "Completada", "Cancelada"],
            width=200,
            dropdown_fg_color="#FFFFFF",
            button_color="#6774BD",
            button_hover_color="#5363BD"
        )
        self.status_combo.pack(side="left", fill="x", expand=True)

        # Filtro por tipo de seguro
        insurance_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        insurance_frame.pack(fill="x", pady=5)

        insurance_label = ctk.CTkLabel(insurance_frame, text="Seguro:", width=80)
        insurance_label.pack(side="left", padx=(0, 10))

        self.insurance_var = ctk.StringVar(value="Todos")
        self.insurance_combo = ctk.CTkComboBox(
            insurance_frame,
            variable=self.insurance_var,
            values=["Todos", "Health", "Auto Insurance", "Long-term Disability", "Life"],
            width=200,
            dropdown_fg_color="#FFFFFF",
            button_color="#6774BD",
            button_hover_color="#5363BD"
        )
        self.insurance_combo.pack(side="left", fill="x", expand=True)

        # Botón de búsqueda
        self.search_button = ctk.CTkButton(
            self.right_panel,
            text="Buscar",
            font=("Roboto", 14),
            fg_color="#6774BD",
            hover_color="#5363BD",
            corner_radius=8,
            command=self.search_appointments
        )
        self.search_button.pack(padx=15, pady=15)

        # Marco para acciones
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=20, pady=(10, 5))

        # Contador de citas seleccionadas
        self.selection_label = ctk.CTkLabel(
            self.action_frame,
            text="10 citas",
            font=("Roboto", 14)
        )
        self.selection_label.pack(side="left")

        # Botones de acción
        button_styles = {
            "font": ("Roboto", 13),
            "corner_radius": 8,
            "height": 32,
            "border_spacing": 5
        }

        self.edit_button = ctk.CTkButton(
            self.action_frame,
            text="Editar",
            fg_color="#6774BD",
            hover_color="#5363BD",
            command=self.edit_appointment,
            **button_styles
        )
        self.edit_button.pack(side="right", padx=5)

        self.cancel_button = ctk.CTkButton(
            self.action_frame,
            text="Cancelar",
            fg_color="#FF5A75",
            hover_color="#E54568",
            command=self.cancel_appointment,
            **button_styles
        )
        self.cancel_button.pack(side="right", padx=5)

        self.email_button = ctk.CTkButton(
            self.action_frame,
            text="Enviar Recordatorio",
            fg_color="#FF9A3D",
            hover_color="#E58B35",
            command=self.send_reminder,
            **button_styles
        )
        self.email_button.pack(side="right", padx=5)

        self.complete_button = ctk.CTkButton(
            self.action_frame,
            text="Completar",
            fg_color="#28C7A2",
            hover_color="#1DAA8B",
            command=self.complete_appointment,
            **button_styles
        )
        self.complete_button.pack(side="right", padx=5)

        # Crear tabla - SOLO EL CONTENEDOR, SIN ENCABEZADOS
        self.table_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Configurar grid con 9 columnas (para coincidir con tus encabezados)
        for i in range(9):
            self.table_frame.grid_columnconfigure(i, weight=1 if i > 0 else 0)

        # Scrollable area para las filas
        self.rows_canvas = ctk.CTkCanvas(self.table_frame, bg="#FFFFFF", highlightthickness=0)
        self.rows_canvas.grid(row=1, column=0, columnspan=9, sticky="nsew")

        self.scrollbar = ctk.CTkScrollbar(self.table_frame, command=self.rows_canvas.yview)
        self.scrollbar.grid(row=1, column=9, sticky="ns")

        self.rows_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.rows_frame = ctk.CTkFrame(self.rows_canvas, fg_color="#FFFFFF")
        self.rows_canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")

        self.rows_frame.bind("<Configure>",
                             lambda e: self.rows_canvas.configure(scrollregion=self.rows_canvas.bbox("all")))

        # Ajustar altura de la tabla
        self.table_frame.grid_rowconfigure(1, weight=1)

    def load_appointments_table(self):
        """Carga las citas en formato de tabla"""

        # Limpiar filas anteriores
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        # Obtener citas filtradas
        appointments = self.appointment_manager.get_filtered_appointments(
            self.filter_values["date"],
            self.filter_values["patient_id"],
            self.filter_values["status"]
        )

        # Mostrar mensaje si no hay citas
        if not appointments:
            no_results = ctk.CTkLabel(
                self.rows_frame,
                text="No hay citas que coincidan con los filtros.",
                font=("Roboto", 14),
                text_color="#585E6A"
            )
            no_results.pack(pady=20)
            return

        # Encabezados de la tabla
        headers = [
            "", "Hora", "Paciente", "Seguro", "Doctor", "Email", "Fecha", "Estado", "Notas"
        ]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.rows_frame,
                text=header,
                font=("Roboto", 12, "bold"),
                anchor="w",
                text_color="#3B3B3B"
            )
            label.grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Colores
        insurance_colors = {
            "health": "#28C7A2",
            "auto insurance": "#6774BD",
            "long-term disability": "#FF9A3D",
            "life": "#FF5A75"
        }

        status_colors = {
            "scheduled": "#52AC66",
            "confirmed": "#28C7A2",
            "completed": "#6774BD",
            "cancelled": "#FF5A75"
        }

        status_text_map = {
            "scheduled": "Programada",
            "confirmed": "Confirmada",
            "completed": "Completada",
            "cancelled": "Cancelada"
        }

        # Crear filas
        for row, appointment in enumerate(appointments, start=1):
            # Checkbox
            check_var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                self.rows_frame,
                text="",
                variable=check_var,
                width=20,
                checkbox_width=20,
                checkbox_height=20,
                command=lambda id=appointment['id'], var=check_var: self.on_appointment_selected(id, var.get())
            )
            checkbox.grid(row=row, column=0, padx=5, pady=5, sticky="w")

            # Hora
            time_label = ctk.CTkLabel(
                self.rows_frame,
                text=f"{appointment['start_time']} - {appointment['end_time']}",
                font=("Roboto", 11),
                anchor="w"
            )
            time_label.grid(row=row, column=1, padx=5, pady=5, sticky="w")

            # Paciente
            patient_name = f"{appointment.get('patient_first_name', '')} {appointment.get('patient_last_name', '')}"
            patient_label = ctk.CTkLabel(
                self.rows_frame,
                text=patient_name,
                font=("Roboto", 11),
                anchor="w"
            )
            patient_label.grid(row=row, column=2, padx=5, pady=5, sticky="w")

            # Seguro
            insurance_type = appointment.get('insurance_type', '')
            insurance_label = ctk.CTkLabel(
                self.rows_frame,
                text=insurance_type.capitalize(),
                font=("Roboto", 11),
                text_color=insurance_colors.get(insurance_type.lower(), "#585E6A"),
                anchor="w"
            )
            insurance_label.grid(row=row, column=3, padx=5, pady=5, sticky="w")

            # Doctor
            doctor_label = ctk.CTkLabel(
                self.rows_frame,
                text=appointment.get('doctor', ''),
                font=("Roboto", 11),
                text_color="#6774BD",
                anchor="w"
            )
            doctor_label.grid(row=row, column=4, padx=5, pady=5, sticky="w")

            # Email
            email_label = ctk.CTkLabel(
                self.rows_frame,
                text=appointment.get('email', ''),
                font=("Roboto", 11),
                text_color="#585E6A",
                anchor="w"
            )
            email_label.grid(row=row, column=5, padx=5, pady=5, sticky="w")

            # Fecha
            date_label = ctk.CTkLabel(
                self.rows_frame,
                text=appointment.get('date', ''),
                font=("Roboto", 11),
                text_color="#585E6A",
                anchor="w"
            )
            date_label.grid(row=row, column=6, padx=5, pady=5, sticky="w")

            # Estado
            status = appointment.get('status', '')
            status_label = ctk.CTkLabel(
                self.rows_frame,
                text=status_text_map.get(status, "Programada"),
                font=("Roboto", 11, "bold"),
                text_color=status_colors.get(status, "#52AC66"),
                anchor="w"
            )
            status_label.grid(row=row, column=7, padx=5, pady=5, sticky="w")

            # Notas
            notes_text = appointment.get('notes', '')
            if len(notes_text) > 30:
                notes_text = notes_text[:27] + "..."
            notes_label = ctk.CTkLabel(
                self.rows_frame,
                text=notes_text,
                font=("Roboto", 11),
                text_color="#585E6A",
                anchor="w"
            )
            notes_label.grid(row=row, column=8, padx=5, pady=5, sticky="w")
            # Alternar color de fondo en filas pares
            if row % 2 == 0:
                for child in self.rows_frame.winfo_children():
                    if child.grid_info().get("row") == row:
                        child.configure(bg_color="#F5F7FA")

    def edit_appointment(self, appointment_id=None):
        """Editar cita (seleccionada o específica)"""
        if appointment_id is None:
            if len(self.selected_appointments) != 1:
                CTkMessagebox(
                    title="Selección",
                    message="Por favor, seleccione exactamente una cita para editar.",
                    icon="warning"
                )
                return
            appointment_id = list(self.selected_appointments)[0]

        self.selected_appointments = {appointment_id}
        self.update_button_states()
        AppointmentDialog(self, "editar", appointment_id)

    def on_date_selected(self, event=None):
        """Maneja la selección de fecha en el calendario"""
        selected_date = self.calendar.get_date()
        self.date_entry.set_date(datetime.strptime(selected_date, "%d/%m/%Y"))
        self.search_appointments()

    def on_date_entry_selected(self, event=None):
        """Maneja la selección de fecha en el entry"""
        selected_date = self.date_entry.get_date()
        self.calendar.selection_set(selected_date)
        self.search_appointments()

    def on_appointment_selected(self, appointment_id, is_selected):
        """Gestiona la selección de una cita"""
        if is_selected:
            self.selected_appointments.add(appointment_id)
        else:
            self.selected_appointments.discard(appointment_id)

        # Actualizar etiqueta de selección
        count = len(self.selected_appointments)
        self.selection_label.configure(text=f"{count} {'cita seleccionada' if count == 1 else 'citas seleccionadas'}")

        # Actualizar estado de botones
        self.update_button_states()

    def update_button_states(self):
        """Actualiza el estado de los botones según la selección"""
        has_selection = len(self.selected_appointments) > 0

        # Botones que requieren selección
        for btn in [self.edit_button, self.cancel_button, self.complete_button, self.email_button]:
            btn.configure(state="normal" if has_selection else "disabled")

        # La edición solo funciona con una selección
        if len(self.selected_appointments) != 1:
            self.edit_button.configure(state="disabled")

    def search_appointments(self):
        """Busca citas según los filtros aplicados"""
        # Obtener fecha seleccionada
        date_str = self.date_entry.get_date().strftime("%Y-%m-%d") if self.date_entry.get_date() else None

        # Obtener paciente seleccionado
        patient_id = None
        if self.patient_var.get() != "Todos":
            # Extraer ID del paciente del texto del combo
            match = re.search(r'ID: (\d+)', self.patient_var.get())
            if match:
                patient_id = int(match.group(1))

        # Obtener estado seleccionado
        status = None
        if self.status_var.get() != "Todos":
            # Mapear estado en español a inglés
            status_map = {
                "Programada": "scheduled",
                "Confirmada": "confirmed",
                "Completada": "completed",
                "Cancelada": "cancelled"
            }
            status = status_map.get(self.status_var.get())

        # Obtener tipo de seguro
        insurance_type = None
        if self.insurance_var.get() != "Todos":
            insurance_type = self.insurance_var.get().lower()

        # Actualizar los valores de filtro
        self.filter_values = {
            "date": date_str,
            "patient_id": patient_id,
            "status": status,
            "insurance_type": insurance_type
        }

        # Cargar citas filtradas en formato de tabla
        self.load_appointments_table()

    def new_appointment(self):
        """Abre el diálogo para crear una nueva cita"""
        dialog = AppointmentDialog(self, mode="nueva")
        dialog.grab_set()  # Previene que se use la ventana principal hasta cerrar el diálogo

    def cancel_appointment(self):
        """Cancela las citas seleccionadas"""
        if not self.selected_appointments:
            CTkMessagebox(title="Selección",
                          message="Por favor, seleccione al menos una cita para cancelar.",
                          icon="warning")
            return

        # Confirmar cancelación
        count = len(self.selected_appointments)
        confirm_msg = f"¿Está seguro que desea cancelar {count} {'cita' if count == 1 else 'citas'}?"

        dialog = CTkMessagebox(title="Confirmar Cancelación",
                               message=confirm_msg,
                               icon="question",
                               option_1="Cancelar",
                               option_2="Confirmar")

        response = dialog.get()
        if response == "Confirmar":
            try:
                # Actualizar estado en la base de datos para cada cita seleccionada
                for appointment_id in self.selected_appointments:
                    success = self.appointment_manager.update_appointment_status(
                        appointment_id,
                        "cancelled"
                    )

                    if not success:
                        CTkMessagebox(title="Error",
                                      message=f"No se pudo cancelar la cita {appointment_id}.",
                                      icon="error")
                        return

                CTkMessagebox(title="Éxito",
                              message=f"{count} {'cita cancelada' if count == 1 else 'citas canceladas'} correctamente.",
                              icon="info")

                # Actualizar tabla
                self.search_appointments()

            except Exception as e:
                CTkMessagebox(title="Error",
                              message=f"Ocurrió un error al cancelar las citas: {str(e)}",
                              icon="error")

    def complete_appointment(self):
        """Marca las citas seleccionadas como completadas"""
        if not self.selected_appointments:
            CTkMessagebox(title="Selección",
                          message="Por favor, seleccione al menos una cita para marcar como completada.",
                          icon="warning")
            return

        try:
            count = len(self.selected_appointments)
            for appointment_id in self.selected_appointments:
                success = self.appointment_manager.update_appointment_status(
                    appointment_id,
                    "completed"
                )

                if not success:
                    CTkMessagebox(title="Error",
                                  message=f"No se pudo completar la cita {appointment_id}.",
                                  icon="error")
                    return

            CTkMessagebox(title="Éxito",
                          message=f"{count} {'cita marcada' if count == 1 else 'citas marcadas'} como completada.",
                          icon="info")

            # Actualizar tabla
            self.search_appointments()

        except Exception as e:
            CTkMessagebox(title="Error",
                          message=f"Ocurrió un error al completar la(s) cita(s): {str(e)}",
                          icon="error")

    def send_reminder(self):
        """Envía recordatorios por email para las citas seleccionadas"""
        if not self.selected_appointments:
            CTkMessagebox(title="Selección",
                          message="Por favor, seleccione al menos una cita para enviar recordatorio.",
                          icon="warning")
            return

        try:
            count = len(self.selected_appointments)
            success_count = 0

            for appointment_id in self.selected_appointments:
                # Obtener datos de la cita
                appointment = self.appointment_manager.get_appointment_by_id(appointment_id)
                if not appointment:
                    continue

                # Obtener datos del paciente
                patient = self.patient_manager.get_patient_by_id(appointment['patient_id'])
                if not patient or not patient.get('email'):
                    continue

                # Enviar email
                send_success = send_appointment_email(
                    to_email=patient['email'],
                    patient_name=f"{patient.get('nombre', '')} {patient.get('apellidos', '')}",
                    appointment_date=appointment['date'],
                    appointment_time=appointment['start_time'],
                    doctor_name=appointment.get('doctor', ''),
                    location=appointment.get('location', '')
                )

                if send_success:
                    success_count += 1

            CTkMessagebox(title="Éxito",
                          message=f"Recordatorios enviados: {success_count} de {count}.",
                          icon="info")

        except Exception as e:
            CTkMessagebox(title="Error",
                          message=f"Ocurrió un error al enviar recordatorios: {str(e)}",
                          icon="error")


class AppointmentDialog(ctk.CTkToplevel):
    """Diálogo para crear/editar citas con diseño o"""

    def __init__(self, parent, mode, appointment_id=None):
        super().__init__(parent)

        self.parent = parent
        self.mode = mode
        self.appointment_id = appointment_id

        # Configuración de la ventana
        self.title("Nueva Cita" if mode == "nueva" else "Editar Cita")
        self.geometry("600x700")
        self.resizable(False, False)

        # Cargar datos si es edición
        self.appointment_data = None
        if mode == "editar":
            self.appointment_data = self.parent.appointment_manager.get_appointment_by_id(appointment_id)
            if not self.appointment_data:
                self.destroy()
                return

        # Configurar interfaz
        self.setup_ui()

        # Centrar diálogo
        self._center_on_parent()

    def _center_on_parent(self):
        """Centra el diálogo sobre la ventana padre"""
        self.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Nueva Cita Médica" if self.mode == "nueva" else "Editar Cita Médica",
            font=("Roboto", 18, "bold"),
            text_color="#6774BD"
        )
        title_label.pack(pady=(10, 20))

        # Marco para el formulario
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=5)

        # Campos del formulario
        self._create_form_fields(form_frame)

        # Botones de acción
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        # Botón Cancelar
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            font=("Roboto", 14),
            fg_color="#FF5A75",
            hover_color="#E54568",
            corner_radius=8,
            command=self.destroy
        )
        cancel_button.pack(side="left", padx=5)

        # Botón Guardar
        save_button = ctk.CTkButton(
            button_frame,
            text="Guardar" if self.mode == "nueva" else "Actualizar",
            font=("Roboto", 14),
            fg_color="#28C7A2",
            hover_color="#1DAA8B",
            corner_radius=8,
            command=self.save_appointment
        )
        save_button.pack(side="right", padx=5)

    def _create_form_fields(self, parent_frame):
        """Crea los campos del formulario de cita"""
        # Paciente
        patient_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        patient_frame.pack(fill="x", pady=5)

        patient_label = ctk.CTkLabel(patient_frame, text="Paciente:", width=120)
        patient_label.pack(side="left", padx=(0, 10))

        self.patient_var = ctk.StringVar()
        self.patient_combo = ctk.CTkComboBox(
            patient_frame,
            variable=self.patient_var,
            width=300,
            values=self._load_patient_options(),
            dropdown_fg_color="#FFFFFF",
            button_color="#6774BD",
            button_hover_color="#5363BD"
        )
        self.patient_combo.pack(side="left", fill="x", expand=True)

        # Fecha
        date_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=5)

        date_label = ctk.CTkLabel(date_frame, text="Fecha:", width=120)
        date_label.pack(side="left", padx=(0, 10))

        self.date_entry = DateEntry(
            date_frame,
            width=12,
            background='#6774BD',
            foreground='white',
            borderwidth=0,
            date_pattern='dd/mm/yyyy'
        )
        self.date_entry.pack(side="left", fill="x", expand=True)

        # Hora de inicio
        start_time_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        start_time_frame.pack(fill="x", pady=5)

        start_time_label = ctk.CTkLabel(start_time_frame, text="Hora de inicio:", width=120)
        start_time_label.pack(side="left", padx=(0, 10))

        self.start_time_var = ctk.StringVar(value="09:00")
        self.start_time_combo = ctk.CTkComboBox(
            start_time_frame,
            variable=self.start_time_var,
            values=[f"{h:02d}:{m:02d}" for h in range(8, 20) for m in [0, 15, 30, 45]],
            width=300,
            dropdown_fg_color="#FFFFFF",
            button_color="#6774BD",
            button_hover_color="#5363BD"
        )
        self.start_time_combo.pack(side="left", fill="x", expand=True)

        # Hora de fin
        end_time_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        end_time_frame.pack(fill="x", pady=5)

        end_time_label = ctk.CTkLabel(end_time_frame, text="Hora de fin:", width=120)
        end_time_label.pack(side="left", padx=(0, 10))

        self.end_time_var = ctk.StringVar(value="09:30")
        self.end_time_combo = ctk.CTkComboBox(
            end_time_frame,
            variable=self.end_time_var,
            values=[f"{h:02d}:{m:02d}" for h in range(8, 20) for m in [0, 15, 30, 45]],
            width=300,
            dropdown_fg_color="#FFFFFF",
            button_color="#6774BD",
            button_hover_color="#5363BD"
        )
        self.end_time_combo.pack(side="left", fill="x", expand=True)

        # Doctor
        doctor_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        doctor_frame.pack(fill="x", pady=5)

        doctor_label = ctk.CTkLabel(doctor_frame, text="Doctor:", width=120)
        doctor_label.pack(side="left", padx=(0, 10))

        self.doctor_var = ctk.StringVar()
        self.doctor_combo = ctk.CTkComboBox(
            doctor_frame,
            variable=self.doctor_var,
            values=["Dr. Kristin", "Dr. Colleen", "Dr. Alex"],
            width=300,
            dropdown_fg_color="#FFFFFF",
            button_color="#6774BD",
            button_hover_color="#5363BD"
        )
        self.doctor_combo.pack(side="left", fill="x", expand=True)

        # Tipo de seguro
        insurance_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        insurance_frame.pack(fill="x", pady=5)

        insurance_label = ctk.CTkLabel(insurance_frame, text="Tipo de seguro:", width=120)
        insurance_label.pack(side="left", padx=(0, 10))

        self.insurance_var = ctk.StringVar(value="Health")
        self.insurance_combo = ctk.CTkComboBox(
            insurance_frame,
            variable=self.insurance_var,
            values=["Health", "Auto Insurance", "Long-term Disability", "Life"],
            width=300,
            dropdown_fg_color="#FFFFFF",
            button_color="#6774BD",
            button_hover_color="#5363BD"
        )
        self.insurance_combo.pack(side="left", fill="x", expand=True)

        # Ubicación
        location_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        location_frame.pack(fill="x", pady=5)

        location_label = ctk.CTkLabel(location_frame, text="Ubicación:", width=120)
        location_label.pack(side="left", padx=(0, 10))

        self.location_var = ctk.StringVar()
        self.location_entry = ctk.CTkEntry(
            location_frame,
            textvariable=self.location_var,
            placeholder_text="Ingrese la dirección del consultorio",
            width=300
        )
        self.location_entry.pack(side="left", fill="x", expand=True)

        # Notas
        notes_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        notes_frame.pack(fill="x", pady=5)

        notes_label = ctk.CTkLabel(notes_frame, text="Notas:", width=120)
        notes_label.pack(side="left", padx=(0, 10))

        self.notes_text = ctk.CTkTextbox(
            notes_frame,
            width=300,
            height=100,
            font=("Roboto", 12),
            fg_color="#FFFFFF",
            border_color="#DCDFE3",
            border_width=1,
            corner_radius=5
        )
        self.notes_text.pack(side="left", fill="x", expand=True)

        # Cargar datos si es edición
        if self.mode == "editar" and self.appointment_data:
            self._load_form_data()

    def _load_patient_options(self):
        """Carga las opciones de pacientes para el combobox"""
        patients = self.parent.patient_manager.get_all_patients()
        return [f"{p['nombre']} {p['apellidos']} (ID: {p['id']})" for p in patients]

    def _load_form_data(self):
        """Carga los datos de la cita en el formulario"""
        if not self.appointment_data:
            return

        # Paciente
        patient = self.parent.patient_manager.get_patient_by_id(self.appointment_data['patient_id'])
        if patient:
            patient_text = f"{patient['nombre']} {patient['apellidos']} (ID: {patient['id']})"
            self.patient_var.set(patient_text)

        # Fecha y hora
        if self.appointment_data.get('date'):
            try:
                date_obj = datetime.strptime(self.appointment_data['date'], "%Y-%m-%d").date()
                self.date_entry.set_date(date_obj)
            except:
                pass

        self.start_time_var.set(self.appointment_data.get('start_time', '09:00'))
        self.end_time_var.set(self.appointment_data.get('end_time', '09:30'))

        # Doctor y seguro
        self.doctor_var.set(self.appointment_data.get('doctor', 'Dr. Kristin'))
        self.insurance_var.set(self.appointment_data.get('insurance_type', 'Health').capitalize())

        # Ubicación y notas
        self.location_var.set(self.appointment_data.get('location', ''))
        self.notes_text.insert("1.0", self.appointment_data.get('notes', ''))

    def save_appointment(self, e=None):
        """Guarda o actualiza la cita"""
        if not self.patient_var.get():
            CTkMessagebox(title="Error", message="Debe seleccionar un paciente.", icon="warning")
            return

        # Extraer ID del paciente
        match = re.search(r'ID: (\d+)', self.patient_var.get())
        if not match:
            CTkMessagebox(title="Error", message="No se pudo identificar al paciente seleccionado.", icon="warning")
            return

        patient_id = int(match.group(1))

        # Preparar datos de la cita
        appointment_data = {
            'patient_id': patient_id,
            'date': self.date_entry.get_date().strftime("%Y-%m-%d"),
            'start_time': self.start_time_var.get(),
            'end_time': self.end_time_var.get(),
            'doctor': self.doctor_var.get(),
            'reason': self.notes_text.get("1.0", "end-1c"),
            'status': 'scheduled'
        }

        try:
            if self.mode == "nueva":
                success = self.parent.appointment_manager.create_appointment(**appointment_data)
                action_msg = "creada"
            else:
                success = self.parent.appointment_manager.update_appointment(self.appointment_id, appointment_data)
                action_msg = "actualizada"

            if success:
                CTkMessagebox(title="Éxito", message=f"Cita {action_msg} correctamente.", icon="info")
                self.parent.search_appointments()
                self.destroy()
            else:
                CTkMessagebox(title="Error", message=f"Ocurrió un error: {str(e)}", icon="cancel")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"Ocurrió un error: {str(e)}", icon="cancel")
