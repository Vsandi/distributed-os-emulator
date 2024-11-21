from emulacion.job import Job
from emulacion.recurso import Recurso, SolicitudRecurso
from typing import List
from multiprocessing import connection

class EstadoSistema:
    def __init__(self, activo:bool, current_job:Job, 
                cola_procesos:list[Job], disconnected_time:float):
        self.activo = activo
        self.current_job = current_job
        self.cola_procesos = cola_procesos
        self.disconnected_time = disconnected_time
    
    def get_carga(self):
        carga = 0
        if self.current_job:
            carga += self.current_job.tiempo - self.current_job.tiempo_completado
        for job in self.cola_procesos:
            carga += job.tiempo - job.tiempo_completado
        return carga

import time
from emulacion.job import Job
from emulacion.recurso import SolicitudRecurso, Recurso
from multiprocessing import connection
from typing import List

class Sistema:
    def __init__(self, nombre: str, recursos: List[Recurso], pipe_trabajos: connection,
                conexion_estado: connection, conexion_solicitudes: connection):
        self.nombre = nombre
        self.recursos = recursos  # Lista de objetos Recurso
        self.pipe_trabajos = pipe_trabajos  # Comunicación con el maestro para recibir trabajos
        self.conexion_estado = conexion_estado  # Comunicación con el maestro para reportar estado
        self.conexion_solicitudes = conexion_solicitudes  # Para enviar solicitudes de recursos
        self.current_job = None  # Trabajo actual en ejecución
        self.recursos_asignados = []  # Recursos asignados al trabajo actual

        # Bucle principal
        while True:
            # Revisar si hay trabajos enviados por el maestro
            if self.pipe_trabajos.poll():  # Si hay algo en el pipe
                job = self.pipe_trabajos.recv()  # Recibir trabajo
                self.recibir_job(job)

            # Actualizar el tiempo del trabajo actual
            if self.current_job:
                self.ejecutar_job()

            # Reportar estado al maestro
            self.reportar_estado()

            # Pausa de 1 segundo
            time.sleep(1)

    # Recibe un trabajo y verifica si se puede ejecutar
    def recibir_job(self, job: Job):
        print(f"{self.nombre} recibió el trabajo {job.nombre}.")
        # Si el trabajo requiere recursos, procesar la solicitud
        if job.recursos:
            if self.solicitar_recursos(job.recursos):
                self.current_job = job
                print(f"{self.nombre} comenzó a procesar el trabajo {job.nombre}.")
            else:
                print(f"{self.nombre} no pudo obtener los recursos para el trabajo {job.nombre}.")
                self.pipe_trabajos.send(job)  # Reenviar el trabajo al maestro
        else:
            # Si no requiere recursos, se asigna directamente
            self.current_job = job
            print(f"{self.nombre} comenzó a procesar el trabajo {job.nombre} (sin recursos).")

    # Solicita los recursos necesarios para ejecutar un trabajo
    def solicitar_recursos(self, recursos: List[str]) -> bool:
        for recurso in recursos:
            solicitud = SolicitudRecurso(self.nombre, recurso)
            self.conexion_solicitudes.put(solicitud)  # Enviar solicitud al maestro
            # Esperar respuesta del maestro sobre disponibilidad
            tiempo_espera = 5  # Máximo n segundos de espera
            while tiempo_espera > 0:
                if recurso in [r.nombre for r in self.recursos if r.len.value == 1]:
                    self.recursos_asignados.append(
                        next(r for r in self.recursos if r.nombre == recurso)
                    )
                    break
                time.sleep(1)
                tiempo_espera -= 1
            else:
                # No se obtuvieron todos los recursos
                print(f"{self.nombre} no obtuvo el recurso {recurso} tras esperar.")

    # Libera todos los recursos asignados al trabajo actual
    def liberar_recursos(self):
        for recurso in self.recursos_asignados:
            recurso.len.value = 0  # Marcar el recurso como disponible
            print(f"{self.nombre} liberó el recurso {recurso.nombre}.")
        self.recursos_asignados = []  # Vaciar la lista de recursos asignados

    # Reduce el tiempo restante del trabajo actual y libera recursos al completarlo
    def ejecutar_job(self):
        # Reducir el tiempo restante del trabajo
        self.current_job.tiempo_completado += 1
        tiempo_restante = self.current_job.tiempo - self.current_job.tiempo_completado
        print(f"{self.nombre} ejecutando {self.current_job.nombre}, tiempo restante: {tiempo_restante}s.")

        # Si el trabajo se terminó
        if tiempo_restante <= 0:
            print(f"{self.nombre} completó el trabajo {self.current_job.nombre}.")
            # Liberar recursos asignados
            for recurso in self.recursos_asignados:
                recurso.len.value = 0
                print(f"{self.nombre} liberó el recurso {recurso.nombre}.")
            self.recursos_asignados = []
            # Notificar al maestro que el trabajo se terminó
            self.conexion_estado.put((self.nombre, self.current_job.nombre))
            self.current_job = None

    # Reporta el estado actual al maestro
    def reportar_estado(self):
        estado = {
            "trabajo_actual": self.current_job.nombre if self.current_job else None,
            "recursos_asignados": [recurso.nombre for recurso in self.recursos_asignados],
        }
        self.conexion_estado.put((self.nombre, estado))