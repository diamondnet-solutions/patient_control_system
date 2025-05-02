# =============================================================================
# Nombre del archivo : main_window.py
# Propósito          : Define la ventana principal de la aplicación de gestión clínica.
# Empresa            : DiamondNetSolutions
# Autor              : Eliazar Noa Llascanoa
# Fecha de creación  : 01/05/2025
# =============================================================================

"""
Ventana principal de la aplicación
"""

# ----------------------------
# Librerías estándar de Python
# ----------------------------
import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------
# Librerías de terceros
# ----------------------------
from PIL import Image, ImageTk

# ----------------------------
# Módulos propios del proyecto
# ----------------------------
from ui.appointments import AppointmentsFrame
from ui.patients import PatientsFrame
from ui.treatments import TreatmentsFrame
from ui.reports import ReportsFrame


class MainWindow:
    def __init__(self, root):
        """Inicializa la ventana principal de la aplicación"""
        self.time_label = None
        self.date_label = None
        self.clock_frame = None
        self.nav_buttons = None
        self.logo_photo = None
        self.root = root
        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Crear marco principal que contiene todo
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Crear área de navegación (barra lateral)
        self.nav_frame = ttk.Frame(self.main_frame, width=200)
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Crear área para mostrar el contenido principal
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configurar el título y logo en la parte superior
        self.setup_title()

        # Agregar los botones de navegación lateral
        self.setup_navigation()

        # Crear marco para mostrar la hora actual
        self.setup_clock()

        # Cargar módulo inicial (citas por defecto)
        self.load_frame("citas")

        # Iniciar actualización del reloj
        self.update_clock()

    def setup_title(self):
        """Configura el título y logo de la aplicación"""
        title_frame = ttk.Frame(self.nav_frame)
        title_frame.pack(fill=tk.X, pady=10)

        # Obtener el directorio raíz del proyecto
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Construir la ruta completa al logo
        logo_path = os.path.join(BASE_DIR, "data", "patient_images", "logo.png")

        try:
            # Si existe el logo, cargarlo y mostrarlo
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((120, 120))
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ttk.Label(title_frame, image=self.logo_photo)
                logo_label.pack(pady=5)
        except Exception:
            # Sí hay error al cargar el logo, usar texto
            pass

        # Mostrar el título de la aplicación
        title_label = ttk.Label(title_frame, text="Sistema Clínico",
                                font=("Arial", 14, "bold"))
        title_label.pack(fill=tk.X, pady=5)

        # Línea separadora entre el título y la navegación
        separator = ttk.Separator(self.nav_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=5)

    def setup_navigation(self):
        """Configura los botones de navegación"""
        # Estilo para los botones
        style = ttk.Style()
        style.configure("Nav.TButton", font=("Arial", 12), padding=10)

        # Botones de navegación
        self.nav_buttons = {
            "citas": ttk.Button(self.nav_frame, text="Citas",
                                command=lambda: self.load_frame("citas"),
                                style="Nav.TButton"),
            "pacientes": ttk.Button(self.nav_frame, text="Pacientes",
                                    command=lambda: self.load_frame("pacientes"),
                                    style="Nav.TButton"),
            "tratamientos": ttk.Button(self.nav_frame, text="Tratamientos",
                                       command=lambda: self.load_frame("tratamientos"),
                                       style="Nav.TButton"),
            "reportes": ttk.Button(self.nav_frame, text="Reportes",
                                   command=lambda: self.load_frame("reportes"),
                                   style="Nav.TButton")
        }

        # Colocar botones
        for button in self.nav_buttons.values():
            button.pack(fill=tk.X, pady=5)

        # Línea separadora inferior
        separator = ttk.Separator(self.nav_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)

    def setup_clock(self):
        """
        Crea y configura el reloj en la parte inferior de la barra lateral.
        Muestra la fecha y la hora actual.
        """
        self.clock_frame = ttk.Frame(self.nav_frame)
        self.clock_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.date_label = ttk.Label(self.clock_frame,
                                    font=("Arial", 10),
                                    text="", anchor=tk.CENTER)
        self.date_label.pack(fill=tk.X)

        self.time_label = ttk.Label(self.clock_frame,
                                    font=("Arial", 12, "bold"),
                                    text="", anchor=tk.CENTER)
        self.time_label.pack(fill=tk.X)

    def update_clock(self):
        """Actualiza el reloj con la hora actual"""
        now = datetime.datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")

        self.date_label.config(text=date_str)
        self.time_label.config(text=time_str)

        # Reprogramar actualización cada 1000 milisegundos (1 segundo)
        self.root.after(1000, self.update_clock)

    def load_frame(self, frame_name):
        """Carga el frame correspondiente en el área de contenido"""
        # Resaltar botón seleccionado
        for name, button in self.nav_buttons.items():
            if name == frame_name:
                button.state(['pressed'])
            else:
                button.state(['!pressed'])

        # Limpiar el área de contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Cargar el marco correspondiente
        if frame_name == "citas":
            AppointmentsFrame(self.content_frame)
        elif frame_name == "pacientes":
            PatientsFrame(self.content_frame)
        elif frame_name == "tratamientos":
            TreatmentsFrame(self.content_frame)
        elif frame_name == "reportes":
            ReportsFrame(self.content_frame)

    def on_close(self):
        """Maneja el evento de cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.root.destroy()
