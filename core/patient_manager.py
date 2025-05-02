# =============================================
# Nombre del archivo: patient_manager.py
# Propósito: Gestión de pacientes en el sistema de control de pacientes
# Empresa: DiamondNetSolutions
# Autor: Eliazar
# Fecha de creación: 30/04/2025
# =============================================

"""
Módulo para la gestión de pacientes en el sistema de control de pacientes.
Permite crear, modificar, eliminar y consultar información de pacientes.
"""
import os
import sys
from typing import Dict, List, Any, Optional

# Asegurar que podemos importar desde el directorio raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import DatabaseManager


class PatientManager:
    """Clase para gestionar los pacientes en el sistema."""

    def __init__(self, db_manager=None):
        """
        Inicializa el gestor de pacientes.

        Args:
            db_manager: Instancia de DatabaseManager (opcional)
        """
        self.db_manager = db_manager or DatabaseManager()

        # Directorio para almacenar fotografías de pacientes
        self.photos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'photos')

        # Crear el directorio si no existe
        if not os.path.exists(self.photos_dir):
            os.makedirs(self.photos_dir)

    def get_all_patients(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los pacientes del sistema.

        Returns:
            Lista de diccionarios con la información de los pacientes
        """
        try:
            query = """
                    SELECT id, \
                           first_name as nombre, \
                           last_name  as apellidos, \
                           birthdate  as fecha_nacimiento, \
                           phone      as telefono, \
                           email, \
                           address    as direccion, \
                           notes      as notas_medicas, \
                           NULL       as foto_path
                    FROM patients
                    ORDER BY last_name, first_name \
                    """

            patients = self.db_manager.execute_query(query, fetch_all=True)

            # Procesar los resultados para asegurar valores por defecto
            for patient in patients:
                for key in ['fecha_nacimiento', 'telefono', 'email', 'direccion', 'notas_medicas', 'foto_path']:
                    if patient.get(key) is None:
                        patient[key] = ''

            return patients

        except Exception as e:
            print(f"Error al obtener pacientes: {e}")
            return []

    def search_patients(self, search_text: str) -> List[Dict[str, Any]]:
        """
        Busca pacientes que coincidan con el texto de búsqueda.

        Args:
            search_text: Texto a buscar en nombres, apellidos, teléfono o email

        Returns:
            Lista de diccionarios con la información de los pacientes que coinciden
        """
        try:
            search_pattern = f"%{search_text}%"

            query = """
                    SELECT id, \
                           first_name as nombre, \
                           last_name  as apellidos, \
                           birthdate  as fecha_nacimiento, \
                           phone      as telefono, \
                           email, \
                           address    as direccion, \
                           notes      as notas_medicas, \
                           NULL       as foto_path
                    FROM patients
                    WHERE first_name LIKE ?
                       OR last_name LIKE ?
                       OR phone LIKE ?
                       OR email LIKE ?
                    ORDER BY last_name, first_name \
                    """

            params = (search_pattern, search_pattern, search_pattern, search_pattern)
            patients = self.db_manager.execute_query(query, params, fetch_all=True)

            # Procesar los resultados para asegurar valores por defecto
            for patient in patients:
                for key in ['fecha_nacimiento', 'telefono', 'email', 'direccion', 'notas_medicas', 'foto_path']:
                    if patient.get(key) is None:
                        patient[key] = ''

            return patients

        except Exception as e:
            print(f"Error al buscar pacientes: {e}")
            return []

    def get_patient_by_id(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene la información de un paciente por su ID.

        Args:
            patient_id: ID del paciente

        Returns:
            Diccionario con la información del paciente o None si no existe
        """
        try:
            query = """
                    SELECT id, \
                           first_name as nombre, \
                           last_name  as apellidos, \
                           birthdate  as fecha_nacimiento, \
                           phone      as telefono, \
                           email, \
                           address    as direccion, \
                           notes      as notas_medicas, \
                           NULL       as foto_path
                    FROM patients
                    WHERE id = ? \
                    """

            patient = self.db_manager.execute_query(query, (patient_id,), fetch_one=True)

            if patient:
                # Asegurar valores por defecto para campos que pueden ser NULL
                for key in ['fecha_nacimiento', 'telefono', 'email', 'direccion', 'notas_medicas', 'foto_path']:
                    if patient.get(key) is None:
                        patient[key] = ''
                return patient
            else:
                return None

        except Exception as e:
            print(f"Error al obtener paciente: {e}")
            return None

    def add_patient(self, patient_data: Dict[str, Any]) -> Optional[int]:
        """
        Agrega un nuevo paciente al sistema.

        Args:
            patient_data: Diccionario con la información del paciente

        Returns:
            ID del paciente creado o None si hubo un error
        """
        try:
            # Mapear los nombres de campos de la interfaz a los nombres de columnas de la BD
            db_data = {
                'first_name': patient_data.get('nombre', ''),
                'last_name': patient_data.get('apellidos', ''),
                'birthdate': patient_data.get('fecha_nacimiento', ''),
                'phone': patient_data.get('telefono', ''),
                'email': patient_data.get('email', ''),
                'address': patient_data.get('direccion', ''),
                'notes': patient_data.get('notas_medicas', '')
            }

            # Usar el método insert_record del DatabaseManager
            return self.db_manager.insert_record('patients', db_data)

        except Exception as e:
            print(f"Error al agregar paciente: {e}")
            return None

    def update_patient(self, patient_data: Dict[str, Any]) -> bool:
        """
        Actualiza la información de un paciente existente.

        Args:
            patient_data: Diccionario con la información actualizada del paciente

        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            patient_id = patient_data.get('id')
            if not patient_id:
                return False

            # Mapear los nombres de campos de la interfaz a los nombres de columnas de la BD
            db_data = {
                'first_name': patient_data.get('nombre', ''),
                'last_name': patient_data.get('apellidos', ''),
                'birthdate': patient_data.get('fecha_nacimiento', ''),
                'phone': patient_data.get('telefono', ''),
                'email': patient_data.get('email', ''),
                'address': patient_data.get('direccion', ''),
                'notes': patient_data.get('notas_medicas', '')
            }

            # Usar el método update_record del DatabaseManager
            return self.db_manager.update_record('patients', patient_id, db_data)

        except Exception as e:
            print(f"Error al actualizar paciente: {e}")
            return False

    def delete_patient(self, patient_id: int) -> bool:
        """
        Elimina un paciente del sistema.

        Args:
            patient_id: ID del paciente a eliminar

        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            # Usar el método delete_record del DatabaseManager
            return self.db_manager.delete_record('patients', patient_id)

        except Exception as e:
            print(f"Error al eliminar paciente: {e}")
            return False