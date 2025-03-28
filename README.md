#  Sistema de Procesamiento de Imágenes Satelitales (Producer-Consumer)

**Implementación robusta del patrón producer-consumer** para procesamiento concurrente de imágenes satelitales con Python, multiprocessing y sincronización segura.


##  Cómo Ejecutar el Sistema

Configuración personalizada en el código:

En el bloque if __name__ == "__main__":
system = ImageProcessingSystem(
    max_buffer_size=10,  # Tamaño del buffer
    num_workers=3        # Número de procesos consumidores
)
