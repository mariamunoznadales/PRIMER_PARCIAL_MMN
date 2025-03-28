#  Sistema de Procesamiento de Imágenes Satelitales (Producer-Consumer)

**Implementación del patrón producer-consumer** para procesamiento concurrente de imágenes satelitales con Python, multiprocessing y sincronización segura.

**Sistema concurrente** que simula recepción/procesamiento de imágenes satelitales usando Python. **Productor** (hilo) genera imágenes a buffer compartido, 

**consumidores** (procesos) las procesan en paralelo. **Buffer FIFO** con sincronización segura. Ejecutar con `python satelite.py` (25 imágenes demo). Stats finales 

automáticos.


##  Cómo Ejecutar el Sistema

Configuración personalizada en el código:

En el bloque if __name__ == "__main__":

system = ImageProcessingSystem(
   
    max_buffer_size=10,  # Tamaño del buffer
   
    num_workers=3        # Número de procesos consumidores

)


