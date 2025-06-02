# =============================================================================
# Nombre del archivo : main_window.py
# Propósito          : Define la ventana principal de la aplicación de gestión clínica.
# Empresa            : DiamondNetSolutions
# Autor              : Eliazar Noa Llascanoa
# Fecha de creación  : 01/05/2025
# =============================================================================

"""
Ventana principal de la aplicación con diseño izado
"""

# ----------------------------
# Librerías estándar de Python
# ----------------------------
import os
import datetime
import tkinter as tk
from tkinter import messagebox

# ----------------------------
# Librerías de terceros
# ----------------------------
import customtkinter as ctk
from PIL import Image, ImageTk
from tkcalendar import Calendar

# ----------------------------
# Módulos propios del proyecto
# ----------------------------
from ui.appointments import AppointmentsFrame
from ui.patients import PatientsFrame
from ui.treatments import TreatmentsFrame
from ui.reports import ReportsFrame

# Configuración de apariencia global de CustomTkinter
ctk.set_appearance_mode("light")  # Modos: "dark", "light"
ctk.set_default_color_theme("green")  # Temas: "blue", "green", "dark-blue"


class MainWindow:
    def __init__(self, root):
        """Inicializa la ventana principal izada de la aplicación"""
        self.main_content = None
        self.root = root
        self.root.title("Sistema Clínico")
        self.root.geometry("1280x720")
        self.root.minsize(1100, 600)

        # Colores de la aplicación
        self.colors = {
            "primary": "#4ECDC4",  # Verde turquesa
            "light_bg": "#E8F5F3",  # Fondo claro verdoso
            "accent": "#FF6B6B",  # Rosa/rojo para acentos
            "text_dark": "#2D3E50",  # Texto oscuro
            "text_light": "#FFFFFF",  # Texto claro
            "sidebar_bg": "#E8F5F3",  # Fondo de la barra lateral
            "selected": "#3BBBB2"  # Color de selección
        }

        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Obtener el directorio raíz del proyecto
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Crear la estructura principal de la aplicación
        self._create_main_layout()

        # Inicializar frames de módulos (pero no mostrarlos todavía)
        self.frames = {}
        self.current_frame = None

        # Cargar el módulo de citas por defecto
        self.load_frame("citas")

        # Iniciar actualización del reloj
        self.update_clock()

    def _create_main_layout(self):
        """Crea el layout principal de la aplicación"""
        # Crear un contenedor principal
        self.main_container = ctk.CTkFrame(self.root, fg_color=self.colors["light_bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Crear la barra lateral (sidebar)
        self._create_sidebar()

        # Crear el área de contenido principal
        self.content_area = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color=self.colors["light_bg"])
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear el frame para el contenido de los módulos
        self.module_frame = ctk.CTkFrame(self.content_area, corner_radius=15, fg_color="#FFFFFF")
        self.module_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_sidebar(self):
        """Crea la barra lateral con navegación y logo"""
        # Frame principal de la barra lateral
        self.sidebar = ctk.CTkFrame(self.main_container, width=220, corner_radius=0, fg_color=self.colors["sidebar_bg"])
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)  # Mantener el ancho fijo

        # Área del logo
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(fill=tk.X, pady=(20, 10))

        # Cargar el logo
        logo_path = os.path.join(self.BASE_DIR, "data", "patient_images", "logo.png")
        try:
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((100, 100))
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            self.logo_label = ctk.CTkLabel(self.logo_frame, image=self.logo_photo, text="")
            self.logo_label.pack(pady=10)
        except Exception:
            # Si hay error al cargar el logo, usar texto
            self.logo_label = ctk.CTkLabel(self.logo_frame, text="Sistema Integral de Gestión Clínica",
                                           font=ctk.CTkFont(family="Arial", size=18, weight="bold"))
            self.logo_label.pack(pady=10)

        # Etiqueta del sistema
        self.app_name_label = ctk.CTkLabel(self.logo_frame, text="Gestión Clínica",
                                           font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                                           text_color=self.colors["text_dark"])
        self.app_name_label.pack(pady=5)

        # Separador
        self.separator = ctk.CTkFrame(self.sidebar, height=2, fg_color=self.colors["primary"])
        self.separator.pack(fill=tk.X, padx=20, pady=10)

        # Botones de navegación
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.pack(fill=tk.X, pady=10)

        # Cargar los iconos para los botones
        self.icons = {}
        icon_size = (24, 24)
        icon_paths = {
            "citas": os.path.join(self.BASE_DIR, "data", "icons", "calendar.png"),
            "pacientes": os.path.join(self.BASE_DIR, "data", "icons", "patients.png"),
            "tratamientos": os.path.join(self.BASE_DIR, "data", "icons", "treatment.png"),
            "reportes": os.path.join(self.BASE_DIR, "data", "icons", "report.png"),
            "perfil": os.path.join(self.BASE_DIR, "data", "icons", "profile.png"),
            "notificaciones": os.path.join(self.BASE_DIR, "data", "icons", "notification.png"),
            "diagnostico": os.path.join(self.BASE_DIR, "data", "icons", "diagnosis.png"),
            "logout": os.path.join(self.BASE_DIR, "data", "icons", "logout.png"),
            "settings": os.path.join(self.BASE_DIR, "data", "icons", "settings.png")
        }

        # Intentar cargar los iconos
        for name, path in icon_paths.items():
            try:
                if os.path.exists(path):
                    img = Image.open(path)
                    img = img.resize(icon_size)
                    self.icons[name] = ImageTk.PhotoImage(img)
                else:
                    self.icons[name] = None
            except Exception:
                self.icons[name] = None

        # Textos para los botones de navegación
        button_texts = {
            "citas": "Calendario",
            "pacientes": "Pacientes",
            "tratamientos": "Tratamientos",
            "reportes": "Reportes",
            "notificaciones": "Notificaciones",
            "perfil": "Mi Perfil",
            "diagnostico": "Diagnosticar",
            "logout": "Cerrar Sesión",
            "settings": "Parámetros"
        }

        # Crear los botones de navegación
        self.nav_buttons = {}
        for name in ["citas", "pacientes", "tratamientos", "reportes", "notificaciones", "perfil"]:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=button_texts[name],
                image=self.icons[name],
                compound="left",
                anchor="w",
                height=40,
                corner_radius=10,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=self.colors["text_dark"],
                hover_color=self.colors["primary"],
                command=lambda n=name: self.load_frame(n)
            )
            btn.pack(fill=tk.X, padx=10, pady=5)
            self.nav_buttons[name] = btn

        # Separador antes de botones especiales
        self.separator2 = ctk.CTkFrame(self.sidebar, height=2, fg_color=self.colors["primary"])
        self.separator2.pack(fill=tk.X, padx=20, pady=10)

        # Botón de diagnóstico especial
        self.diagnostico_btn = ctk.CTkButton(
            self.sidebar,
            text=button_texts["diagnostico"],
            image=self.icons["diagnostico"],
            compound="left",
            anchor="w",
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["primary"],
            text_color=self.colors["text_light"],
            hover_color=self.colors["selected"],
            command=lambda: print("Diagnóstico con IA")
        )
        self.diagnostico_btn.pack(fill=tk.X, padx=10, pady=5)

        # Frame para el reloj en la parte inferior
        self.clock_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.clock_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Etiquetas para la fecha y hora
        self.date_label = ctk.CTkLabel(
            self.clock_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_dark"]
        )
        self.date_label.pack(fill=tk.X, pady=(0, 5))

        self.time_label = ctk.CTkLabel(
            self.clock_frame,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        self.time_label.pack(fill=tk.X)

        # Botones en la parte inferior
        self.bottom_buttons_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.bottom_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Botón de cerrar sesión
        self.logout_btn = ctk.CTkButton(
            self.bottom_buttons_frame,
            text=button_texts["logout"],
            image=self.icons["logout"],
            compound="left",
            anchor="w",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=self.colors["text_dark"],
            hover_color=self.colors["accent"],
            command=self.on_close
        )
        self.logout_btn.pack(fill=tk.X, pady=5)

        # Botón de configuración
        self.settings_btn = ctk.CTkButton(
            self.bottom_buttons_frame,
            text=button_texts["settings"],
            image=self.icons["settings"],
            compound="left",
            anchor="w",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=self.colors["text_dark"],
            hover_color=self.colors["primary"],
            command=lambda: print("Configuración")
        )
        self.settings_btn.pack(fill=tk.X, pady=5)

    def update_clock(self):
        """Actualiza el reloj con la hora actual"""
        now = datetime.datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")

        self.date_label.configure(text=date_str)
        self.time_label.configure(text=time_str)

        # Reprogramar actualización cada 1000 milisegundos (1 segundo)
        self.root.after(1000, self.update_clock)

    def load_frame(self, frame_name):
        """Carga el frame correspondiente en el área de contenido"""
        # Actualizar estado visual de los botones
        for name, button in self.nav_buttons.items():
            if name == frame_name:
                button.configure(fg_color=self.colors["primary"], text_color=self.colors["text_light"])
            else:
                button.configure(fg_color="transparent", text_color=self.colors["text_dark"])

        # Limpiar el área de contenido
        for widget in self.module_frame.winfo_children():
            widget.destroy()

        # Frame de título del módulo
        title_frame = ctk.CTkFrame(self.module_frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, padx=20, pady=10)

        # Título del módulo correspondiente
        module_titles = {
            "citas": "Calendario de Citas",
            "pacientes": "Gestión de Pacientes",
            "tratamientos": "Catálogo de Tratamientos",
            "reportes": "Reportes y Estadísticas",
            "notificaciones": "Centro de Notificaciones",
            "perfil": "Mi Perfil Profesional"
        }

        module_title_label = ctk.CTkLabel(
            title_frame,
            text=module_titles.get(frame_name, ""),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        module_title_label.pack(anchor="w")

        # Separador
        separator = ctk.CTkFrame(self.module_frame, height=2, fg_color=self.colors["primary"])
        separator.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Contenedor para el contenido del módulo
        module_content = ctk.CTkFrame(self.module_frame, fg_color="transparent")
        module_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Cargar el módulo correspondiente
        if frame_name == "citas":
            AppointmentsFrame(module_content)
        elif frame_name == "pacientes":
            PatientsFrame(module_content)
        elif frame_name == "tratamientos":
            TreatmentsFrame(module_content)
        elif frame_name == "reportes":
            ReportsFrame(module_content)
        elif frame_name == "notificaciones":
            self._load_notifications_module(module_content)
        elif frame_name == "perfil":
            self._load_profile_module(module_content)

    def _load_calendar_module(self, parent):
        """Carga el módulo de calendario de citas"""
        # Frame superior con controles de navegación del calendario
        calendar_controls = ctk.CTkFrame(parent, fg_color="transparent")
        calendar_controls.pack(fill=tk.X, pady=(0, 10))

        # Etiqueta del mes actual (ejemplo: ABRIL 2023)
        now = datetime.datetime.now()
        month_names = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
                       "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        current_month_name = month_names[now.month - 1]

        month_label = ctk.CTkLabel(
            calendar_controls,
            text=f"{current_month_name} {now.year}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        month_label.pack(side=tk.LEFT)

        # Botones para navegar entre meses
        nav_buttons_frame = ctk.CTkFrame(calendar_controls, fg_color="transparent")
        nav_buttons_frame.pack(side=tk.LEFT, padx=20)

        prev_month_btn = ctk.CTkButton(
            nav_buttons_frame,
            text="<",
            width=30,
            height=30,
            corner_radius=15,
            fg_color=self.colors["primary"],
            hover_color=self.colors["selected"],
            text_color=self.colors["text_light"],
            command=lambda: print("Mes anterior")
        )
        prev_month_btn.pack(side=tk.LEFT, padx=5)

        next_month_btn = ctk.CTkButton(
            nav_buttons_frame,
            text=">",
            width=30,
            height=30,
            corner_radius=15,
            fg_color=self.colors["primary"],
            hover_color=self.colors["selected"],
            text_color=self.colors["text_light"],
            command=lambda: print("Mes siguiente")
        )
        next_month_btn.pack(side=tk.LEFT, padx=5)

        # Botones de filtro de vista (Mes, Semana, Día)
        view_filters = ctk.CTkSegmentedButton(
            calendar_controls,
            values=["MOIS", "SEMAINE", "JOUR"],
            selected_color=self.colors["primary"],
            unselected_color=self.colors["light_bg"],
            text_color=self.colors["text_dark"],
            selected_hover_color=self.colors["selected"],
            command=lambda value: print(f"Vista: {value}")
        )
        view_filters.pack(side=tk.RIGHT)
        view_filters.set("MOIS")  # Seleccionar vista por defecto

        # Frame para el calendario
        calendar_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=10)
        calendar_frame.pack(fill=tk.BOTH, expand=True)

        # Implementar el calendario utilizando tkcalendar
        # (Esto es un ejemplo básico, en una implementación real se podría personalizar más)
        cal = Calendar(
            calendar_frame,
            selectmode="day",
            year=now.year,
            month=now.month,
            showweeknumbers=False,
            firstweekday="sunday",
            background=self.colors["light_bg"],
            foreground=self.colors["text_dark"],
            bordercolor=self.colors["light_bg"],
            headersbackground=self.colors["primary"],
            headersforeground=self.colors["text_light"],
            normalbackground="#FFFFFF",
            weekendbackground="#F5F5F5",
            othermonthbackground="#EEEEEE",
            othermonthforeground="#AAAAAA",
            selectbackground=self.colors["accent"],
            font=("Arial", 10)
        )
        cal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Días con citas (esto es un ejemplo, en una aplicación real se cargarían de la base de datos)
        cal.calevent_create(datetime.datetime(now.year, now.month, 3), "Citas", "reminder")
        cal.calevent_create(datetime.datetime(now.year, now.month, 7), "Citas", "reminder")
        cal.calevent_create(datetime.datetime(now.year, now.month, 12), "Citas", "reminder")
        cal.calevent_create(datetime.datetime(now.year, now.month, 21), "Citas", "reminder")
        cal.calevent_create(datetime.datetime(now.year, now.month, 28), "Citas", "reminder")
        cal.tag_config("reminder", background=self.colors["accent"], foreground="white")

    def _load_notifications_module(self, parent):
        """Carga el módulo de notificaciones"""
        # Frame para el contenido de notificaciones
        notifications_frame = ctk.CTkFrame(parent, fg_color="transparent")
        notifications_frame.pack(fill=tk.BOTH, expand=True)

        # Título del módulo
        title_label = ctk.CTkLabel(
            notifications_frame,
            text="Centro de Notificaciones",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Ejemplos de notificaciones
        notification_types = [
            {"title": "Cita cancelada", "text": "El paciente Carlos Méndez ha cancelado su cita para hoy",
             "time": "10:30", "color": self.colors["accent"]},
            {"title": "Recordatorio", "text": "Reunión de equipo a las 14:00", "time": "12:15",
             "color": self.colors["primary"]},
            {"title": "Mensaje nuevo", "text": "Tiene un nuevo mensaje del Dr. García", "time": "Ayer",
             "color": self.colors["selected"]}
        ]

        for notification in notification_types:
            self._add_notification(notifications_frame, notification)

    def _add_notification(self, parent, notification):
        """Agrega una notificación al panel de notificaciones"""
        notification_frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="#FFFFFF", height=80)
        notification_frame.pack(fill=tk.X, pady=5)
        notification_frame.pack_propagate(False)

        # Indicador de color para el tipo de notificación
        indicator = ctk.CTkFrame(notification_frame, width=5, corner_radius=2, fg_color=notification["color"])
        indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)

        # Contenido de la notificación
        content_frame = ctk.CTkFrame(notification_frame, fg_color="transparent")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=5)

        title_label = ctk.CTkLabel(
            content_frame,
            text=notification["title"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_dark"],
            anchor="w"
        )
        title_label.pack(anchor="w")

        text_label = ctk.CTkLabel(
            content_frame,
            text=notification["text"],
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_dark"],
            anchor="w"
        )
        text_label.pack(anchor="w", pady=(5, 0))

        # Tiempo de la notificación
        time_label = ctk.CTkLabel(
            notification_frame,
            text=notification["time"],
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_dark"]
        )
        time_label.pack(side=tk.RIGHT, padx=10)

    def _load_profile_module(self, parent):
        """Carga el módulo de perfil de usuario"""
        # Frame para el contenido del perfil
        profile_frame = ctk.CTkFrame(parent, fg_color="transparent")
        profile_frame.pack(fill=tk.BOTH, expand=True)

        # Sección superior con foto e información básica
        top_section = ctk.CTkFrame(profile_frame, fg_color="#FFFFFF", corner_radius=15)
        top_section.pack(fill=tk.X, pady=10)

        # Intentar cargar una imagen de perfil
        profile_pic_path = os.path.join(self.BASE_DIR, "data", "patient_images", "doctor.png")
        try:
            if os.path.exists(profile_pic_path):
                profile_img = Image.open(profile_pic_path)
                profile_img = profile_img.resize((120, 120))
                self.profile_photo = ImageTk.PhotoImage(profile_img)
                profile_pic = ctk.CTkLabel(top_section, image=self.profile_photo, text="")
                profile_pic.pack(side=tk.LEFT, padx=20, pady=20)
            else:
                # Si no hay imagen, mostrar un placeholder
                profile_pic = ctk.CTkLabel(
                    top_section,
                    text="DR",
                    width=120,
                    height=120,
                    corner_radius=60,
                    fg_color=self.colors["primary"],
                    text_color=self.colors["text_light"],
                    font=ctk.CTkFont(size=36, weight="bold")
                )
                profile_pic.pack(side=tk.LEFT, padx=20, pady=20)
        except Exception as e:
            print(f"Error al cargar imagen de perfil: {e}")
            # Placeholder en caso de error
            profile_pic = ctk.CTkLabel(
                top_section,
                text="DR",
                width=120,
                height=120,
                corner_radius=60,
                fg_color=self.colors["primary"],
                text_color=self.colors["text_light"],
                font=ctk.CTkFont(size=36, weight="bold")
            )
            profile_pic.pack(side=tk.LEFT, padx=20, pady=20)

        # Información del perfil
        info_frame = ctk.CTkFrame(top_section, fg_color="transparent")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=20)

        # Nombre del doctor
        name_label = ctk.CTkLabel(
            info_frame,
            text="Dr. Eliazar Noa Llascanoa",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        name_label.pack(anchor="w", pady=(0, 5))

        # Especialidad
        specialty_label = ctk.CTkLabel(
            info_frame,
            text="Odontología General",
            font=ctk.CTkFont(size=16),
            text_color=self.colors["text_dark"]
        )
        specialty_label.pack(anchor="w", pady=(0, 10))

        # Estadísticas
        stats_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        stats_frame.pack(anchor="w")

        stats = [
            {"value": "1,248", "label": "Pacientes"},
            {"value": "98%", "label": "Satisfacción"},
            {"value": "5", "label": "Años Exp."}
        ]

        for stat in stats:
            stat_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.pack(side=tk.LEFT, padx=20)

            value_label = ctk.CTkLabel(
                stat_frame,
                text=stat["value"],
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=self.colors["primary"]
            )
            value_label.pack()

            label_label = ctk.CTkLabel(
                stat_frame,
                text=stat["label"],
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_dark"]
            )
            label_label.pack()

        # Botón de editar perfil
        edit_btn = ctk.CTkButton(
            top_section,
            text="Editar Perfil",
            width=120,
            height=40,
            corner_radius=10,
            fg_color=self.colors["primary"],
            hover_color=self.colors["selected"],
            text_color=self.colors["text_light"],
            command=lambda: print("Editar perfil")
        )
        edit_btn.pack(side=tk.RIGHT, padx=20, pady=20)

        # Sección de pestañas
        self.profile_tabs = ctk.CTkTabview(profile_frame, fg_color="transparent")
        self.profile_tabs.pack(fill=tk.BOTH, expand=True, pady=10)

        # Añadir pestañas
        self.profile_tabs.add("Información")
        self.profile_tabs.add("Horario")
        self.profile_tabs.add("Configuración")

        # Contenido de la pestaña de Información
        self._load_profile_info_tab(self.profile_tabs.tab("Información"))

        # Contenido de la pestaña de Horario
        self._load_schedule_tab(self.profile_tabs.tab("Horario"))

        # Contenido de la pestaña de Configuración
        self._load_settings_tab(self.profile_tabs.tab("Configuración"))

    def _load_profile_info_tab(self, tab):
        """Carga el contenido de la pestaña de información del perfil"""
        # Frame para formulario de información
        form_frame = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=15)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Campos del formulario
        fields = [
            {"label": "Nombre Completo", "value": "Eliazar Noa Llascanoa"},
            {"label": "Correo Electrónico", "value": "eliazar@diamondnetsolutions.com"},
            {"label": "Teléfono", "value": "+51 987 654 321"},
            {"label": "Especialidad", "value": "Odontología General"},
            {"label": "N° Colegiatura", "value": "CP12345"},
            {"label": "Dirección Consultorio", "value": "Av. Dental 123, Lima"}
        ]

        for i, field in enumerate(fields):
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.pack(fill=tk.X, padx=20, pady=10)

            label = ctk.CTkLabel(
                row_frame,
                text=field["label"] + ":",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors["text_dark"],
                width=200,
                anchor="e"
            )
            label.pack(side=tk.LEFT, padx=(0, 10))

            value = ctk.CTkLabel(
                row_frame,
                text=field["value"],
                font=ctk.CTkFont(size=14),
                text_color=self.colors["text_dark"],
                anchor="w"
            )
            value.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Sección de biografía
        bio_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        bio_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        bio_label = ctk.CTkLabel(
            bio_frame,
            text="Biografía:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        bio_label.pack(anchor="w")

        bio_text = ctk.CTkTextbox(
            form_frame,
            height=120,
            font=ctk.CTkFont(size=14),
            fg_color="#F5F5F5",
            text_color=self.colors["text_dark"],
            wrap=tk.WORD
        )
        bio_text.pack(fill=tk.X, padx=20, pady=(0, 20))
        bio_text.insert("1.0", "Especialista en odontología general con más de 5 años de experiencia...")
        bio_text.configure(state="disabled")

    def _load_schedule_tab(self, tab):
        """Carga el contenido de la pestaña de horario"""
        # Frame principal
        schedule_frame = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=15)
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        title_label = ctk.CTkLabel(
            schedule_frame,
            text="Horario de Atención",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        title_label.pack(pady=20)

        # Días de la semana
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        for day in days:
            day_frame = ctk.CTkFrame(schedule_frame, fg_color="transparent")
            day_frame.pack(fill=tk.X, padx=40, pady=5)

            # Checkbox para día activo
            active_var = ctk.BooleanVar(value=(day != "Domingo"))  # Domingo inactivo por defecto
            active_cb = ctk.CTkCheckBox(
                day_frame,
                text="",
                variable=active_var,
                width=20,
                command=lambda d=day: self._toggle_day(d)
            )
            active_cb.pack(side=tk.LEFT, padx=(0, 10))

            # Nombre del día
            day_label = ctk.CTkLabel(
                day_frame,
                text=day,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors["text_dark"],
                width=100,
                anchor="w"
            )
            day_label.pack(side=tk.LEFT)

            # Horario de mañana
            morning_frame = ctk.CTkFrame(day_frame, fg_color="transparent")
            morning_frame.pack(side=tk.LEFT, padx=10)

            morning_label = ctk.CTkLabel(
                morning_frame,
                text="Mañana:",
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_dark"]
            )
            morning_label.pack(side=tk.LEFT)

            morning_start = ctk.CTkComboBox(
                morning_frame,
                values=[f"{h:02d}:00" for h in range(6, 13)],
                width=80,
                state="readonly"
            )
            morning_start.pack(side=tk.LEFT, padx=5)
            morning_start.set("08:00")

            morning_end = ctk.CTkComboBox(
                morning_frame,
                values=[f"{h:02d}:00" for h in range(6, 13)],
                width=80,
                state="readonly"
            )
            morning_end.pack(side=tk.LEFT, padx=5)
            morning_end.set("12:00")

            # Horario de tarde
            afternoon_frame = ctk.CTkFrame(day_frame, fg_color="transparent")
            afternoon_frame.pack(side=tk.LEFT, padx=10)

            afternoon_label = ctk.CTkLabel(
                afternoon_frame,
                text="Tarde:",
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_dark"]
            )
            afternoon_label.pack(side=tk.LEFT)

            afternoon_start = ctk.CTkComboBox(
                afternoon_frame,
                values=[f"{h:02d}:00" for h in range(12, 20)],
                width=80,
                state="readonly"
            )
            afternoon_start.pack(side=tk.LEFT, padx=5)
            afternoon_start.set("14:00")

            afternoon_end = ctk.CTkComboBox(
                afternoon_frame,
                values=[f"{h:02d}:00" for h in range(12, 20)],
                width=80,
                state="readonly"
            )
            afternoon_end.pack(side=tk.LEFT, padx=5)
            afternoon_end.set("18:00")

        # Botón para guardar horario
        save_btn = ctk.CTkButton(
            schedule_frame,
            text="Guardar Horario",
            width=200,
            height=40,
            corner_radius=10,
            fg_color=self.colors["primary"],
            hover_color=self.colors["selected"],
            text_color=self.colors["text_light"],
            command=self._save_schedule
        )
        save_btn.pack(pady=20)

    def _load_settings_tab(self, tab):
        """Carga el contenido de la pestaña de configuración"""
        # Frame principal
        settings_frame = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=15)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configuración de notificaciones
        notif_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        notif_frame.pack(fill=tk.X, padx=20, pady=20)

        notif_label = ctk.CTkLabel(
            notif_frame,
            text="Configuración de Notificaciones",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        notif_label.pack(anchor="w", pady=(0, 10))

        # Opciones de notificación
        notif_options = [
            {"text": "Recordatorios de citas", "var": tk.BooleanVar(value=True)},
            {"text": "Nuevos mensajes", "var": tk.BooleanVar(value=True)},
            {"text": "Resultados de laboratorio", "var": tk.BooleanVar(value=False)},
            {"text": "Promociones y ofertas", "var": tk.BooleanVar(value=False)}
        ]

        for option in notif_options:
            cb = ctk.CTkCheckBox(
                notif_frame,
                text=option["text"],
                variable=option["var"],
                text_color=self.colors["text_dark"]
            )
            cb.pack(anchor="w", padx=20, pady=5)

        # Separador
        separator = ctk.CTkFrame(settings_frame, height=2, fg_color=self.colors["light_bg"])
        separator.pack(fill=tk.X, padx=20, pady=10)

        # Configuración de privacidad
        privacy_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        privacy_frame.pack(fill=tk.X, padx=20, pady=20)

        privacy_label = ctk.CTkLabel(
            privacy_frame,
            text="Configuración de Privacidad",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        privacy_label.pack(anchor="w", pady=(0, 10))

        # Opciones de privacidad
        privacy_options = [
            {"text": "Mostrar perfil público", "var": tk.BooleanVar(value=True)},
            {"text": "Permitir mensajes directos", "var": tk.BooleanVar(value=True)},
            {"text": "Mostrar disponibilidad en línea", "var": tk.BooleanVar(value=False)}
        ]

        for option in privacy_options:
            cb = ctk.CTkCheckBox(
                privacy_frame,
                text=option["text"],
                variable=option["var"],
                text_color=self.colors["text_dark"]
            )
            cb.pack(anchor="w", padx=20, pady=5)

        # Botón para guardar configuración
        save_btn = ctk.CTkButton(
            settings_frame,
            text="Guardar Configuración",
            width=200,
            height=40,
            corner_radius=10,
            fg_color=self.colors["primary"],
            hover_color=self.colors["selected"],
            text_color=self.colors["text_light"],
            command=self._save_settings
        )
        save_btn.pack(pady=20)

    def _toggle_day(self, day):
        """Activa/desactiva un día en el horario"""
        print(f"Cambiando estado para {day}")

    def _save_schedule(self):
        """Guarda el horario configurado"""
        messagebox.showinfo("Horario", "Horario guardado correctamente")

    def _save_settings(self):
        """Guarda la configuración del usuario"""
        messagebox.showinfo("Configuración", "Configuración guardada correctamente")

    def on_close(self):
        """Maneja el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir de la aplicación?"):
            self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = MainWindow(root)
    root.mainloop()