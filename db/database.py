# database.py
"""
Módulo de conexión y operaciones de base de datos para el sistema de gestión clínica.

Archivo: database.py
Propósito: Manejar todas las operaciones de base de datos para el sistema de gestión de pacientes, citas y tratamientos.
Empresa: DiamondNetSolutions
Autor: Eliazar
Fecha de creación: 01/05/2025
"""

import datetime
# =============================================
# Importaciones
# =============================================
# Librerías estándar de Python
import os
import sqlite3
from typing import Dict, List, Any, Union

# =============================================
# Configuración global
# =============================================
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    'data', 
    'clinic.db'
)

# =============================================
# Funciones de utilidad para transacciones
# =============================================
def rollback_transaction(conn: sqlite3.Connection) -> None:
    """
    Revierte una transacción manual en caso de error.
    
    Args:
        conn (sqlite3.Connection): Objeto de conexión activa a la base de datos
    """
    conn.rollback()
    conn.close()


def commit_transaction(conn: sqlite3.Connection) -> None:
    """
    Confirma y finaliza una transacción manual exitosa.
    
    Args:
        conn (sqlite3.Connection): Objeto de conexión activa a la base de datos
    """
    conn.commit()
    conn.close()


# =============================================
# Clase principal DatabaseManager
# =============================================
class DatabaseManager:
    """
    Clase principal para gestionar todas las operaciones de base de datos.
    
    Proporciona métodos para:
    - Crear y mantener la estructura de la base de datos
    - Ejecutar consultas genéricas
    - Gestionar transacciones
    - Realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    - Generar backups de la base de datos
    """
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Inicializa el gestor de base de datos.
        
        Args:
            db_path (str): Ruta al archivo de base de datos SQLite. 
                          Por defecto usa DB_PATH global.
        """
        self.db_path = db_path
        self._ensure_data_dir()
        self.setup_database()

    def _ensure_data_dir(self) -> None:
        """Verifica y crea el directorio de datos si no existe."""
        data_dir = os.path.dirname(self.db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def get_connection(self) -> sqlite3.Connection:
        """
        Establece y retorna una nueva conexión a la base de datos.
        
        Returns:
            sqlite3.Connection: Objeto de conexión configurado para acceder 
                               a las columnas por nombre (row_factory)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceso a columnas por nombre
        return conn

    def setup_database(self) -> None:
        """Crea todas las tablas necesarias si no existen."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla de pacientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birthdate TEXT,
                gender TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        # Tabla de citas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT DEFAULT 'scheduled',
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')

        # Tabla de categorías de tratamientos
        cursor.execute('''
           CREATE TABLE IF NOT EXISTS treatment_categories
           (
               id          INTEGER PRIMARY KEY AUTOINCREMENT,
               name        TEXT NOT NULL,
               description TEXT,
               active      INTEGER DEFAULT 1,
               created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
           )
        ''')

        # Tabla de tratamientos (versión mejorada)
        cursor.execute('''
           CREATE TABLE IF NOT EXISTS treatments
           (
               id            INTEGER PRIMARY KEY AUTOINCREMENT,
               category_id   INTEGER,
               name          TEXT NOT NULL,
               description   TEXT,
               default_price REAL NOT NULL DEFAULT 0,
               duration      INTEGER       DEFAULT 30,
               active        INTEGER       DEFAULT 1,
               created_at    TEXT          DEFAULT CURRENT_TIMESTAMP,
               updated_at    TEXT          DEFAULT CURRENT_TIMESTAMP,
               FOREIGN KEY (category_id) REFERENCES treatment_categories (id)
           )
        ''')

        # Tabla de historial de precios de tratamientos
        cursor.execute('''
           CREATE TABLE IF NOT EXISTS treatment_price_history
           (
               id           INTEGER PRIMARY KEY AUTOINCREMENT,
               treatment_id INTEGER NOT NULL,
               price        REAL    NOT NULL,
               start_date   TEXT    NOT NULL,
               end_date     TEXT,
               created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
               FOREIGN KEY (treatment_id) REFERENCES treatments (id)
           )
        ''')

        # Tabla de tratamientos aplicados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointment_treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER,
                treatment_id INTEGER,
                quantity INTEGER DEFAULT 1,
                price_applied REAL NOT NULL,
                notes TEXT,
                FOREIGN KEY (appointment_id) REFERENCES appointments (id),
                FOREIGN KEY (treatment_id) REFERENCES treatments (id)
            )
        ''')

        # Tabla de pagos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER,
                amount REAL NOT NULL,
                payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
                payment_method TEXT,
                notes TEXT,
                FOREIGN KEY (appointment_id) REFERENCES appointments (id)
            )
        ''')

        # Tabla de historial médico
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                record_date TEXT DEFAULT CURRENT_TIMESTAMP,
                symptoms TEXT,
                diagnosis TEXT,
                treatment_plan TEXT,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')

        # Tabla de configuración de email
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smtp_server TEXT NOT NULL,
                smtp_port INTEGER NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                sender_email TEXT NOT NULL,
                sender_name TEXT,
                signature TEXT
            )
        ''')

        # Tabla de plantillas de email
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                active INTEGER DEFAULT 1
            )
        ''')

        # Tabla de horarios de trabajo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_of_week INTEGER,
                start_time TEXT,
                end_time TEXT,
                is_working_day INTEGER DEFAULT 1
            )
        ''')

        # Tabla de seguimiento de emails
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER,
                sent_date TEXT DEFAULT CURRENT_TIMESTAMP,
                email_type TEXT,
                recipient_email TEXT,
                status TEXT DEFAULT 'sent',
                response_date TEXT,
                response_content TEXT,
                FOREIGN KEY (appointment_id) REFERENCES appointments (id)
            )
        ''')

        conn.commit()
        conn.close()

    def execute_query(
        self, 
        query: str, 
        params: tuple = None,
        fetch_all: bool = False, 
        fetch_one: bool = False,
        return_last_id: bool = False
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], int, bool]:
        """
        Método genérico para ejecutar consultas SQL.
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple): Parámetros para la consulta (opcional)
            fetch_all (bool): Si True, retorna todos los resultados
            fetch_one (bool): Si True, retorna solo el primer resultado
            return_last_id (bool): Si True, retorna el ID del último insert
            
        Returns:
            Depende de los parámetros:
            - fetch_all: Lista de diccionarios
            - fetch_one: Un diccionario o None
            - return_last_id: Entero con último ID
            - Por defecto: Booleano indicando éxito
            
        Raises:
            sqlite3.Error: Si ocurre un error en la base de datos
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch_all:
                results = cursor.fetchall()
                conn.commit()
                return [dict(row) for row in results]

            elif fetch_one:
                result = cursor.fetchone()
                conn.commit()
                return dict(result) if result else None

            elif return_last_id:
                conn.commit()
                return cursor.lastrowid

            else:
                conn.commit()
                return True

        except sqlite3.Error as e:
            conn.rollback()
            raise sqlite3.Error(f"Error en la base de datos: {e}")
        finally:
            conn.close()

    def get_table_data(
        self, 
        table_name: str, 
        conditions: Dict[str, Any] = None,
        order_by: str = None, 
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene datos de una tabla con condiciones opcionales.
        
        Args:
            table_name (str): Nombre de la tabla
            conditions (dict): Condiciones WHERE {columna: valor}
            order_by (str): Columna para ordenar
            limit (int): Límite de resultados
            
        Returns:
            List[dict]: Resultados en formato lista de diccionarios
        """
        query = f"SELECT * FROM {table_name}"
        params = ()

        if conditions:
            query += " WHERE " + " AND ".join([f"{k} = ?" for k in conditions.keys()])
            params = tuple(conditions.values())

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query, params, fetch_all=True)

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        Inserta un nuevo registro en la tabla especificada.
        
        Args:
            table_name (str): Nombre de la tabla
            data (dict): Datos a insertar {columna: valor}
            
        Returns:
            int: ID del nuevo registro insertado
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        return self.execute_query(query, tuple(data.values()), return_last_id=True)

    def update_record(
        self, 
        table_name: str, 
        record_id: int, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Actualiza un registro existente.
        
        Args:
            table_name (str): Nombre de la tabla
            record_id (int): ID del registro a actualizar
            data (dict): Datos a actualizar {columna: valor}
            
        Returns:
            bool: True si la actualización fue exitosa
        """
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        
        values = list(data.values()) + [record_id]
        return self.execute_query(query, tuple(values))

    def delete_record(self, table_name: str, record_id: int) -> bool:
        """
        Elimina un registro de la tabla.
        
        Args:
            table_name (str): Nombre de la tabla
            record_id (int): ID del registro a eliminar
            
        Returns:
            bool: True si la eliminación fue exitosa
        """
        query = f"DELETE FROM {table_name} WHERE id = ?"
        return self.execute_query(query, (record_id,))

    def begin_transaction(self) -> sqlite3.Connection:
        """
        Inicia una transacción manual.
        
        Returns:
            sqlite3.Connection: Conexión para gestionar la transacción
            
        Nota: Debe usarse con commit_transaction/rollback_transaction
        """
        return self.get_connection()

    def get_backup(self, backup_path: str = None) -> bool:
        """
        Crea una copia de seguridad de la base de datos.
        
        Args:
            backup_path (str): Ruta personalizada para el backup
            
        Returns:
            bool: True si el backup fue exitoso
            
        Raises:
            RuntimeError: Si falla la creación del backup
        """
        try:
            if not backup_path:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
                
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)

                backup_path = os.path.join(backup_dir, f"clinic_backup_{timestamp}.db")

            with sqlite3.connect(self.db_path) as source_conn, \
                 sqlite3.connect(backup_path) as backup_conn:
                source_conn.backup(backup_conn)
                
            return True
        except Exception as e:
            raise RuntimeError(f"Error al crear backup: {e}")