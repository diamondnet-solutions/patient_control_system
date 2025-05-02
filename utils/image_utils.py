from PIL import Image, ImageOps
import os
import shutil
import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='image_utils.log'
)
logger = logging.getLogger('image_utils')


def resize_image(image, size, maintain_aspect=True):
    """
    Redimensiona una imagen manteniendo la relación de aspecto por defecto.

    Args:
        image (PIL.Image): Imagen a redimensionar
        size (tuple): Tamaño deseado (ancho, alto)
        maintain_aspect (bool): Si se debe mantener la relación de aspecto

    Returns:
        ImageTk.PhotoImage: Imagen redimensionada lista para mostrar en Tkinter
    """
    try:
        if maintain_aspect:
            # Crear una copia para no modificar la original
            img_copy = image.copy()

            # Redimensionar manteniendo la relación de aspecto
            img_copy.thumbnail(size, Image.LANCZOS)

            # Crear fondo blanco del tamaño exacto
            background = Image.new('RGBA', size, (255, 255, 255, 0))

            # Calcular posición centrada
            offset = ((size[0] - img_copy.width) // 2,
                      (size[1] - img_copy.height) // 2)

            # Pegar la imagen redimensionada en el fondo
            background.paste(img_copy, offset)

            # Convertir a formato compatible con Tkinter
            from PIL import ImageTk
            return ImageTk.PhotoImage(background)
        else:
            # Redimensionar la imagen sin mantener la relación de aspecto
            resized = image.resize(size, Image.LANCZOS)
            from PIL import ImageTk
            return ImageTk.PhotoImage(resized)

    except Exception as e:
        logger.error(f"Error al redimensionar imagen: {str(e)}")
        raise


def save_image(source_path, destination_path, optimize=True, quality=85):
    """
    Guarda una imagen en el destino especificado con optimización.

    Args:
        source_path (str): Ruta de la imagen original
        destination_path (str): Ruta donde guardar la imagen
        optimize (bool): Si se debe optimizar la imagen
        quality (int): Calidad de la imagen (0-100)

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    try:
        # Asegurar que el directorio de destino exista
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Si las rutas son iguales, hacer una copia
        if source_path == destination_path:
            shutil.copy2(source_path, destination_path)
            return True

        # Abrir la imagen
        image = Image.open(source_path)

        # Convertir a RGB si es necesario (para JPEG)
        if image.mode != 'RGB' and destination_path.lower().endswith(('.jpg', '.jpeg')):
            image = image.convert('RGB')

        # Guardar la imagen con optimización
        image.save(destination_path, optimize=optimize, quality=quality)
        logger.info(f"Imagen guardada correctamente: {destination_path}")

        return True
    except Exception as e:
        logger.error(f"Error al guardar imagen: {str(e)}")
        return False


def crop_image(image_path, output_path, box):
    """
    Recorta una imagen.

    Args:
        image_path (str): Ruta de la imagen a recortar
        output_path (str): Ruta donde guardar la imagen recortada
        box (tuple): Coordenadas de recorte (left, upper, right, lower)

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    try:
        image = Image.open(image_path)
        cropped = image.crop(box)
        cropped.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Error al recortar imagen: {str(e)}")
        return False


def apply_filter(image_path, output_path, filter_type='GRAYSCALE'):
    """
    Aplica un filtro a una imagen.

    Args:
        image_path (str): Ruta de la imagen original
        output_path (str): Ruta donde guardar la imagen filtrada
        filter_type (str): Tipo de filtro a aplicar (GRAYSCALE, SEPIA, etc.)

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    try:
        image = Image.open(image_path)

        if filter_type == 'GRAYSCALE':
            filtered = ImageOps.grayscale(image)
        elif filter_type == 'SEPIA':
            # Implementación simple de un filtro sepia
            grayscale = ImageOps.grayscale(image)
            sepia = Image.new('RGB', grayscale.size, (0, 0, 0))
            for x in range(grayscale.width):
                for y in range(grayscale.height):
                    gray_pixel = grayscale.getpixel((x, y))
                    # Fórmula para el efecto sepia
                    r = min(int(gray_pixel * 1.1), 255)
                    g = min(int(gray_pixel * 0.9), 255)
                    b = min(int(gray_pixel * 0.7), 255)
                    sepia.putpixel((x, y), (r, g, b))
            filtered = sepia
        else:
            # Si no se reconoce el filtro, devolver la imagen original
            filtered = image

        filtered.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Error al aplicar filtro a imagen: {str(e)}")
        return False


def get_image_metadata(image_path):
    """
    Obtiene metadatos de una imagen.

    Args:
        image_path (str): Ruta de la imagen

    Returns:
        dict: Diccionario con los metadatos de la imagen
    """
    try:
        image = Image.open(image_path)
        metadata = {
            'format': image.format,
            'size': image.size,
            'mode': image.mode,
            'info': image.info
        }

        # Intentar obtener metadatos EXIF si están disponibles
        if hasattr(image, '_getexif') and image._getexif():
            metadata['exif'] = image._getexif()

        return metadata
    except Exception as e:
        logger.error(f"Error al obtener metadatos de imagen: {str(e)}")
        return None


def create_thumbnail_for_patient(source_path, patient_id, size=(150, 150)):
    """
    Crea una miniatura para un paciente específico.

    Args:
        source_path (str): Ruta de la imagen original
        patient_id (int): ID del paciente
        size (tuple): Tamaño de la miniatura

    Returns:
        str: Ruta de la miniatura creada
    """
    try:
        # Crear directorio para miniaturas si no existe
        thumbnails_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'thumbnails'))
        os.makedirs(thumbnails_dir, exist_ok=True)

        # Generar nombre para la miniatura
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        thumbnail_path = os.path.join(thumbnails_dir, f"patient_{patient_id}_{timestamp}_thumb.jpg")

        # Abrir imagen y crear miniatura
        image = Image.open(source_path)
        image.thumbnail(size, Image.LANCZOS)

        # Guardar miniatura
        image.save(thumbnail_path, optimize=True, quality=85)
        logger.info(f"Miniatura creada correctamente: {thumbnail_path}")

        return thumbnail_path
    except Exception as e:
        logger.error(f"Error al crear miniatura para paciente: {str(e)}")
        return None


def get_default_profile_image(size=(150, 150)):
    """
    Crea una imagen de perfil predeterminada para pacientes sin foto.

    Args:
        size (tuple): Tamaño de la imagen

    Returns:
        PIL.ImageTk.PhotoImage: Imagen predeterminada lista para mostrar en Tkinter
    """
    try:
        # Crear imagen básica
        image = Image.new('RGB', size, color=(240, 240, 240))

        # Dibujar silueta básica
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)

        # Círculo para la cabeza
        head_center = (size[0] // 2, size[1] // 3)
        head_radius = size[0] // 5
        draw.ellipse((head_center[0] - head_radius,
                      head_center[1] - head_radius,
                      head_center[0] + head_radius,
                      head_center[1] + head_radius),
                     fill=(200, 200, 200))

        # Cuerpo
        body_points = [
            (size[0] // 2 - head_radius, size[1] // 2),  # hombro izquierdo
            (size[0] // 2 + head_radius, size[1] // 2),  # hombro derecho
            (size[0] // 2 + head_radius + 10, size[1]),  # pie derecho
            (size[0] // 2 - head_radius - 10, size[1])  # pie izquierdo
        ]
        draw.polygon(body_points, fill=(180, 180, 180))

        # Convertir a formato compatible con Tkinter
        from PIL import ImageTk
        return ImageTk.PhotoImage(image)
    except Exception as e:
        logger.error(f"Error al crear imagen de perfil predeterminada: {str(e)}")
        return None