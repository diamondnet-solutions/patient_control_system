# =============================================
# HEADER INFORMATION
# =============================================
# Nombre del archivo: treatment_manager.py
# Propósito: Gestión de tratamientos
# Empresa: DiamondNetSolutions
# Autor: Eliazar
# Fecha de creación: 01-05-2025
# =============================================



"""
Módulo para la gestión de tratamientos
"""

import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('treatment_manager')


class TreatmentManager:
    """Clase para gestionar los tratamientos en el sistema"""

    def __init__(self, db_manager=None):
        """
        Inicializa el gestor de tratamientos

        Args:
            db_manager (DatabaseManager): Instancia del gestor de base de datos
        """
        self.db_manager = db_manager

    def add_treatment_category(self, name, description=None):
        """
        Añade una nueva categoría de tratamiento

        Args:
            name (str): Nombre de la categoría
            description (str, optional): Descripción de la categoría

        Returns:
            int: ID de la categoría creada o None si ocurrió un error
        """
        try:
            data = {
                'name': name,
                'description': description
            }
            category_id = self.db_manager.insert_record('treatment_categories', data)
            logger.info(f"Categoría de tratamiento creada con ID: {category_id}")
            return category_id
        except Exception as e:
            logger.error(f"Error al crear categoría de tratamiento: {e}")
            return None

    def get_all_categories(self, active_only=True):
        """
        Obtiene todas las categorías de tratamientos

        Args:
            active_only (bool): Si es True, solo devuelve categorías activas

        Returns:
            list: Lista de diccionarios con los datos de las categorías
        """
        try:
            conditions = {'active': 1} if active_only else None
            return self.db_manager.get_table_data(
                'treatment_categories',
                conditions=conditions,
                order_by='name'
            )
        except Exception as e:
            logger.error(f"Error al obtener categorías de tratamiento: {e}")
            return []

    def add_treatment(self, name, default_price, category_id=None, description=None, duration=30):
        """
        Añade un nuevo tratamiento

        Args:
            name (str): Nombre del tratamiento
            default_price (float): Precio por defecto del tratamiento
            category_id (int, optional): ID de la categoría
            description (str, optional): Descripción del tratamiento
            duration (int, optional): Duración en minutos del tratamiento

        Returns:
            int: ID del tratamiento creado o None si ocurrió un error
        """
        try:
            # Insertar tratamiento
            treatment_data = {
                'name': name,
                'category_id': category_id,
                'description': description,
                'default_price': default_price,
                'duration': duration
            }

            treatment_id = self.db_manager.insert_record('treatments', treatment_data)

            # Registrar precio inicial en historial
            current_date = datetime.now().strftime('%Y-%m-%d')
            self.db_manager.insert_record('treatment_price_history', {
                'treatment_id': treatment_id,
                'price': default_price,
                'start_date': current_date
            })

            logger.info(f"Tratamiento creado con ID: {treatment_id}")
            return treatment_id
        except Exception as e:
            logger.error(f"Error al crear tratamiento: {e}")
            return None

    def update_treatment(self, treatment_id, name=None, category_id=None,
                         description=None, default_price=None, duration=None, active=None):
        """
        Actualiza los datos de un tratamiento

        Args:
            treatment_id (int): ID del tratamiento a actualizar
            name (str, optional): Nuevo nombre
            category_id (int, optional): Nueva categoría
            description (str, optional): Nueva descripción
            default_price (float, optional): Nuevo precio
            duration (int, optional): Nueva duración
            active (bool, optional): Estado activo/inactivo

        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Obtener datos actuales
            current_data = self.db_manager.execute_query(
                "SELECT * FROM treatments WHERE id = ?",
                (treatment_id,),
                fetch_one=True
            )

            if not current_data:
                logger.warning(f"Tratamiento con ID {treatment_id} no encontrado")
                return False

            # Preparar datos para actualización
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if category_id is not None:
                update_data['category_id'] = category_id
            if description is not None:
                update_data['description'] = description
            if duration is not None:
                update_data['duration'] = duration
            if active is not None:
                update_data['active'] = 1 if active else 0

            # Actualizar marca de tiempo
            update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Si hay precio nuevo, actualizar historial
            if default_price is not None and default_price != current_data['default_price']:
                update_data['default_price'] = default_price

                # Cerrar precio anterior en historial
                current_date = datetime.now().strftime('%Y-%m-%d')
                self.db_manager.execute_query('''
                    UPDATE treatment_price_history
                    SET end_date = ?
                    WHERE treatment_id = ? AND end_date IS NULL
                ''', (current_date, treatment_id))

                # Registrar nuevo precio
                self.db_manager.insert_record('treatment_price_history', {
                    'treatment_id': treatment_id,
                    'price': default_price,
                    'start_date': current_date
                })

            if update_data:
                self.db_manager.update_record('treatments', treatment_id, update_data)
                logger.info(f"Tratamiento con ID {treatment_id} actualizado correctamente")
                return True
            else:
                logger.info(f"No se realizaron cambios en el tratamiento {treatment_id}")
                return False
        except Exception as e:
            logger.error(f"Error al actualizar tratamiento: {e}")
            return False

    def get_all_treatments(self, active_only=True, category_id=None):
        """
        Obtiene todos los tratamientos, opcionalmente filtrados por categoría

        Args:
            active_only (bool): Si es True, solo devuelve tratamientos activos
            category_id (int, optional): ID de categoría para filtrar

        Returns:
            list: Lista de diccionarios con los datos de los tratamientos
        """
        try:
            conditions = {'active': 1} if active_only else {}
            if category_id:
                conditions['category_id'] = category_id

            query = '''
                SELECT t.*, c.name as category_name
                FROM treatments t
                LEFT JOIN treatment_categories c ON t.category_id = c.id
            '''

            if conditions:
                where_clause = " AND ".join([f"t.{k} = ?" for k in conditions.keys()])
                query += f" WHERE {where_clause}"
                params = tuple(conditions.values())
            else:
                params = ()

            query += " ORDER BY t.name"

            return self.db_manager.execute_query(query, params, fetch_all=True)
        except Exception as e:
            logger.error(f"Error al obtener tratamientos: {e}")
            return []

    def get_treatment_by_id(self, treatment_id):
        """
        Obtiene un tratamiento por su ID

        Args:
            treatment_id (int): ID del tratamiento

        Returns:
            dict: Datos del tratamiento o None si no existe
        """
        try:
            query = '''
                SELECT t.*, c.name as category_name
                FROM treatments t
                LEFT JOIN treatment_categories c ON t.category_id = c.id
                WHERE t.id = ?
            '''
            result = self.db_manager.execute_query(query, (treatment_id,), fetch_one=True)
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error al obtener tratamiento por ID: {e}")
            return None

    def assign_treatment_to_appointment(self, appointment_id, treatment_id, price=None, notes=None):
        """
        Asigna un tratamiento a una cita

        Args:
            appointment_id (int): ID de la cita
            treatment_id (int): ID del tratamiento
            price (float, optional): Precio específico para este tratamiento en esta cita
            notes (str, optional): Notas adicionales

        Returns:
            int: ID de la asignación o None si ocurrió un error
        """
        try:
            # Si no se especifica precio, usar el precio por defecto
            if price is None:
                treatment = self.get_treatment_by_id(treatment_id)
                if not treatment:
                    logger.error(f"Tratamiento con ID {treatment_id} no encontrado")
                    return None
                price = treatment['default_price']

            data = {
                'appointment_id': appointment_id,
                'treatment_id': treatment_id,
                'price_applied': price,
                'notes': notes
            }

            assignment_id = self.db_manager.insert_record('appointment_treatments', data)
            logger.info(f"Tratamiento {treatment_id} asignado a cita {appointment_id}")
            return assignment_id
        except Exception as e:
            logger.error(f"Error al asignar tratamiento a cita: {e}")
            return None

    def get_treatments_by_appointment(self, appointment_id):
        """
        Obtiene todos los tratamientos asignados a una cita

        Args:
            appointment_id (int): ID de la cita

        Returns:
            list: Lista de tratamientos asignados a la cita
        """
        try:
            query = '''
                SELECT at.*, t.name as treatment_name, 
                       t.description, t.duration, c.name as category_name
                FROM appointment_treatments at
                JOIN treatments t ON at.treatment_id = t.id
                LEFT JOIN treatment_categories c ON t.category_id = c.id
                WHERE at.appointment_id = ?
                ORDER BY at.id
            '''
            return self.db_manager.execute_query(query, (appointment_id,), fetch_all=True)
        except Exception as e:
            logger.error(f"Error al obtener tratamientos por cita: {e}")
            return []

    def remove_treatment_from_appointment(self, assignment_id):
        """
        Elimina un tratamiento asignado a una cita

        Args:
            assignment_id (int): ID de la asignación tratamiento-cita

        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            result = self.db_manager.delete_record('appointment_treatments', assignment_id)
            if result:
                logger.info(f"Tratamiento desasignado correctamente (ID: {assignment_id})")
            else:
                logger.warning(f"No se encontró asignación con ID {assignment_id}")
            return result
        except Exception as e:
            logger.error(f"Error al eliminar tratamiento de cita: {e}")
            return False

    def get_treatment_price_history(self, treatment_id):
        """
        Obtiene el historial de precios de un tratamiento

        Args:
            treatment_id (int): ID del tratamiento

        Returns:
            list: Historial de precios del tratamiento
        """
        try:
            query = '''
                SELECT *
                FROM treatment_price_history
                WHERE treatment_id = ?
                ORDER BY start_date DESC
            '''
            return self.db_manager.execute_query(query, (treatment_id,), fetch_all=True)
        except Exception as e:
            logger.error(f"Error al obtener historial de precios: {e}")
            return []

    def get_treatments_by_patient(self, patient_id):
        """
        Obtiene todos los tratamientos realizados a un paciente

        Args:
            patient_id (int): ID del paciente

        Returns:
            list: Lista de tratamientos realizados al paciente
        """
        try:
            query = '''
                SELECT at.*, t.name as treatment_name, a.date, a.status
                FROM appointment_treatments at
                JOIN appointments a ON at.appointment_id = a.id
                JOIN treatments t ON at.treatment_id = t.id
                WHERE a.patient_id = ?
                ORDER BY a.date DESC, a.start_time DESC
            '''
            return self.db_manager.execute_query(query, (patient_id,), fetch_all=True)
        except Exception as e:
            logger.error(f"Error al obtener tratamientos por paciente: {e}")
            return []

    def get_popular_treatments(self, start_date=None, end_date=None, limit=10):
        """
        Obtiene los tratamientos más populares en un periodo

        Args:
            start_date (str, optional): Fecha de inicio (YYYY-MM-DD)
            end_date (str, optional): Fecha de fin (YYYY-MM-DD)
            limit (int): Número máximo de resultados

        Returns:
            list: Lista de tratamientos más populares con conteo
        """
        try:
            query = '''
                SELECT t.id, t.name, COUNT(at.id) as count, SUM(at.price_applied) as total_revenue
                FROM appointment_treatments at
                JOIN appointments a ON at.appointment_id = a.id
                JOIN treatments t ON at.treatment_id = t.id
                WHERE a.status = 'completed'
            '''
            params = []

            if start_date:
                query += " AND a.date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND a.date <= ?"
                params.append(end_date)

            query += '''
                GROUP BY t.id
                ORDER BY count DESC
                LIMIT ?
            '''
            params.append(limit)

            return self.db_manager.execute_query(query, params, fetch_all=True)
        except Exception as e:
            logger.error(f"Error al obtener tratamientos populares: {e}")
            return []

    def calculate_treatment_revenue(self, treatment_id=None, start_date=None, end_date=None):
        """
        Calcula los ingresos por tratamientos en un periodo

        Args:
            treatment_id (int, optional): ID del tratamiento específico o None para todos
            start_date (str, optional): Fecha de inicio (YYYY-MM-DD)
            end_date (str, optional): Fecha de fin (YYYY-MM-DD)

        Returns:
            float: Total de ingresos por tratamientos
        """
        try:
            query = '''
                SELECT SUM(at.price_applied) as total
                FROM appointment_treatments at
                JOIN appointments a ON at.appointment_id = a.id
                WHERE a.status = 'completed'
            '''
            params = []

            if treatment_id:
                query += " AND at.treatment_id = ?"
                params.append(treatment_id)

            if start_date:
                query += " AND a.date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND a.date <= ?"
                params.append(end_date)

            result = self.db_manager.execute_query(query, params, fetch_one=True)
            return result['total'] if result and result['total'] else 0
        except Exception as e:
            logger.error(f"Error al calcular ingresos por tratamientos: {e}")
            return 0