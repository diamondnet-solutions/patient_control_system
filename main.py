"""
Archivo: main.py
Propósito: Archivo principal que inicializa y ejecuta la interfaz gráfica del sistema de control de pacientes,
           manejando la carga inicial, la configuración visual y la conexión con la base de datos.
Empresa: DiamondNetSolutions
Autor: Eliazar
Fecha de creación: 01/05/2025
"""

# ========================== #
#        LIBRERÍAS           #
# ========================== #

# Librerías estándar de Python
import tkinter as tk
from tkinter import ttk, messagebox

# Librerías propias del proyecto
from ui.main_window import MainWindow
from db.database import DatabaseManager

# ========================== #
#       FUNCIÓN MAIN         #
# ========================== #

def main():
    """
    Función principal que configura e inicia la aplicación gráfica del sistema.
    Realiza las siguientes tareas:
    - Configura el estilo visual y la ventana principal.
    - Inicializa la base de datos.
    - Carga la ventana principal de la aplicación.
    - Inicia el bucle principal de la interfaz gráfica.
    """

    # Crear la ventana principal usando Tkinter
    root = tk.Tk()
    root.title("Sistema de Control de Pacientes")
    root.geometry("1200x700")  # Tamaño inicial de la ventana

    # ========================== #
    #   CONFIGURACIÓN DE ESTILO  #
    # ========================== #

    # Se define un tema visual agradable
    style = ttk.Style()
    style.theme_use('clam')  # Tema visual: 'clam' es moderno y claro

    # Se configuran los estilos para los distintos widgets
    style.configure('TFrame', background='#f0f0f0')  # Color de fondo para los marcos
    style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))  # Etiquetas
    style.configure('TButton', font=('Arial', 10), background='#4CAF50')  # Botones

    # ========================== #
    #  INICIALIZACIÓN DE LA DB   #
    # ========================== #

    try:
        # Se crea una instancia del gestor de base de datos
        db_manager = DatabaseManager()
        db_manager.setup_database()  # Se crea la base de datos y tablas si no existen
    except Exception as e:
        # Si ocurre un error en la creación o conexión a la base de datos, se muestra un mensaje al usuario
        messagebox.showerror("Error de Base de Datos",
                             f"No se pudo inicializar la base de datos: {str(e)}")
        return  # Se termina la ejecución si hay errores

    # ========================== #
    #     VENTANA PRINCIPAL      #
    # ========================== #

    # Se crea e inicializa la ventana principal de la aplicación
    app = MainWindow(root)  # noqa: F841

    # ========================== #
    #   INICIO DE LA APLICACIÓN  #
    # ========================== #

    # Se inicia el bucle principal de Tkinter, que mantiene la aplicación abierta
    root.mainloop()

# ========================== #
#  PUNTO DE ENTRADA DEL APP  #
# ========================== #

if __name__ == "__main__":
    # Ejecutar la aplicación si el archivo se ejecuta directamente
    main()
