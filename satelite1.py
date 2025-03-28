"""
Implementación del patrón producer-consumer con:
- Un productor que genera imágenes satelitales
- Buffer compartido seguro
- Múltiples consumidores que procesan en paralelo
- Sincronización adecuada
"""

import threading
import time
import random
import multiprocessing
import queue
from dataclasses import dataclass
from datetime import datetime
from collections import deque


@dataclass
class SatelliteImage:
    """Contenedor para imágenes satelitales con metadatos"""
    id: str
    satellite_source: str
    timestamp: str
    data: bytes


class ImageProcessingSystem:
    def __init__(self, max_buffer_size=10, num_workers=3):
        """
        Inicializa el sistema con:
        - max_buffer_size: Tamaño máximo del buffer
        - num_workers: Número de procesos consumidores
        """
        # Buffer compartido (estructura FIFO)
        self.buffer = deque(maxlen=max_buffer_size)
        
        # Cola IPC para comunicación entre procesos
        self.task_queue = multiprocessing.Queue()
        
        # Eventos para control de ejecución
        self.stop_event = multiprocessing.Event()
        self.producer_finished = multiprocessing.Event()
        
        # Pool de workers
        self.workers = []
        self.num_workers = num_workers
        
        # Contadores compartidos
        self.processed_count = multiprocessing.Value('i', 0)
        self.dropped_count = multiprocessing.Value('i', 0)
        
        # Locks para sincronización
        self.buffer_lock = multiprocessing.Lock()
        self.counter_lock = multiprocessing.Lock()

    def start_workers(self):
        """Inicia los procesos workers (consumidores)"""
        for _ in range(self.num_workers):
            # Pasar explícitamente todos los argumentos necesarios
            worker = multiprocessing.Process(
                target=self._worker_consumer,
                args=(
                    self.task_queue,
                    self.stop_event,
                    self.processed_count,
                    self.counter_lock
                )
            )
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
            print(f"Worker {worker.pid} iniciado")

    @staticmethod
    def _worker_consumer(task_queue, stop_event, processed_count, counter_lock):
        """
        Lógica del consumidor (procesa imágenes de la cola)
        Args:
            task_queue: Cola de tareas compartida
            stop_event: Señal de parada
            processed_count: Contador de imágenes procesadas
            counter_lock: Lock para el contador
        """
        while not stop_event.is_set():
            try:
                # Obtener imagen de la cola
                image = task_queue.get(timeout=1)
                
                # Simular procesamiento
                print(f"[Worker {multiprocessing.current_process().pid}] Procesando {image.id}...")
                time.sleep(random.uniform(1, 3))
                
                # Actualizar contador
                with counter_lock:
                    processed_count.value += 1
                    print(f"[Worker {multiprocessing.current_process().pid}] Completo: {image.id}")
                    
            except queue.Empty:
                continue

    def receive_image(self, image):
        """Almacena imágenes en el buffer de forma segura"""
        with self.buffer_lock:
            if len(self.buffer) < self.buffer.maxlen:
                self.buffer.append(image)
                print(f"Imagen {image.id} almacenada (Buffer: {len(self.buffer)}/{self.buffer.maxlen})")
            else:
                with self.counter_lock:
                    self.dropped_count.value += 1
                print(f"Buffer lleno") # No se puede hacer un buffer ilimitado pero seria lo ideal...

    def process_images_from_buffer(self):
        """Transfiere imágenes del buffer a la cola de procesamiento"""
        while not self.stop_event.is_set() or (self.producer_finished.is_set() and len(self.buffer) > 0):
            with self.buffer_lock:
                if len(self.buffer) > 0:
                    image = self.buffer.popleft()
                    self.task_queue.put(image)
            time.sleep(0.1)

    def start_receiving(self, num_images=25):
        """Genera imágenes de ejemplo (productor)"""
        sources = ["SAT-1", "SAT-2", "SAT-3"]
        for i in range(num_images):
            if self.stop_event.is_set():
                break
                
            time.sleep(random.uniform(0.1, 0.5))
            
            new_image = SatelliteImage(
                id=f"IMG-{i:04d}",
                satellite_source=random.choice(sources),
                timestamp=datetime.now().isoformat(),
                data=bytes([random.randint(0, 255) for _ in range(1024)])
            )
            
            self.receive_image(new_image)
        
        self.producer_finished.set()

    def stop(self):
        """Detiene el sistema de forma ordenada"""
        self.stop_event.set()
        for worker in self.workers:
            worker.terminate()

    def get_stats(self):
        """Obtiene estadísticas del sistema"""
        return {
            "processed": self.processed_count.value,
            "dropped": self.dropped_count.value,
            "in_buffer": len(self.buffer)
        }


if __name__ == "__main__":
    print("=== SISTEMA DE PROCESAMIENTO SATELITAL ===")
    system = ImageProcessingSystem(max_buffer_size=10, num_workers=3)
    
    try:
        # Iniciar workers (consumidores)
        system.start_workers()
        
        # Hilo productor
        producer_thread = threading.Thread(
            target=system.start_receiving,
            args=(25,)  # 25 imágenes de ejemplo
        )
        
        # Hilo coordinador
        processor_thread = threading.Thread(
            target=system.process_images_from_buffer
        )
        
        producer_thread.start()
        processor_thread.start()
        
        producer_thread.join()
        processor_thread.join()
        
        # Estadísticas finales
        print("\n=== ESTADÍSTICAS FINALES ===")
        stats = system.get_stats()
        print(f"Imágenes procesadas: {stats['processed']}")
        print(f"Imágenes descartadas: {stats['dropped']}")
        print(f"Imágenes en buffer: {stats['in_buffer']}")
        
    except KeyboardInterrupt:
        print("\nDeteniendo el sistema...")
    finally:
        system.stop()