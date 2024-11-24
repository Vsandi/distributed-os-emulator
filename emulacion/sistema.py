import time
from emulacion.job import Job
from emulacion.recurso import SolicitudRecurso, Recurso
from multiprocessing import connection, Queue
from typing import List

class EstadoSistema:
    def __init__(self):
        self.activo = False
        self.current_job:Job = None
        self.cola_procesos:List[Job] = []
        self.disconnected_time:int = 0
    
    def get_carga(self):
        carga = 0
        if self.current_job:
            carga += self.current_job.get_tiempo_faltante()
        for job in self.cola_procesos:
            carga += job.get_tiempo_faltante()
        return carga


class Sistema:
    def __init__(self, nombre: str, recursos: List[Recurso], pipe_trabajos: connection,
                conexion_estado: connection, conexion_solicitudes: connection, cola_recursos_asignados: Queue):
        self.nombre = nombre
        self.estado = EstadoSistema()
        self.recursos = recursos  # Lista de objetos Recurso
        self.pipe_trabajos = pipe_trabajos  # Comunicación con el maestro para recibir trabajos
        self.conexion_estado = conexion_estado  # Comunicación con el maestro para reportar estado
        self.conexion_solicitudes = conexion_solicitudes  # Para enviar solicitudes de recursos
        self.cola_recursos_asignados = cola_recursos_asignados # Para recibir asignacion de recursos
        self.recursos_asignados = []  # Recursos asignados al trabajo actual

        # Bucle principal
        while True:
            # Recibir recursos del maestro:
            while not self.cola_recursos_asignados.empty():
                recurso = self.cola_recursos_asignados.get()
                self.recursos_asignados.append(recurso)

            # Revisar si hay trabajos enviados por el maestro
            while self.pipe_trabajos.poll():  # Si hay algo en el pipe
                job = self.pipe_trabajos.recv()  # Recibir trabajo
                self.estado.cola_procesos.append(job)

            # Revisar si hay trabajos en espera y el sistema esta inactivo:
            if not self.estado.activo and len(self.estado.cola_procesos) != 0:
                job = self.estado.cola_procesos.pop()
                self.recibir_job(job)
            
            # Actualizar el tiempo del trabajo actual
            if self.estado.activo:
                self.ejecutar_job()

            # Reportar estado al maestro
            self.reportar_estado()

            # Pausa de 1 segundo
            time.sleep(1)

    # Recibe un trabajo y verifica si se puede ejecutar
    def recibir_job(self, job: Job):
        # Si el trabajo requiere recursos, ver si estan o mandar la solicitud
        if len(job.recursos) > 0:

            if not self.__recursosSuficientes(job):
                # Si no tiene los recursos, se solicitan
                self.solicitar_recursos(job.recursos)
                self.estado.cola_procesos.append(job)
            else:
                # Si tiene los recursos se actua
                self.estado.current_job = job
                self.estado.activo = True
        else:
            # Si no requiere recursos, se asigna directamente
            self.estado.current_job = job
            self.estado.activo = True

    # Solicita los recursos necesarios para ejecutar un trabajo
    def solicitar_recursos(self, recursos):
        for recurso in recursos:
            solicitud = SolicitudRecurso(self.nombre, recurso.nombre)
            self.conexion_solicitudes.put(solicitud)

    # Libera todos los recursos asignados al trabajo actual
    def liberar_recursos(self):
        for recurso in self.recursos_asignados:
            solicitud = SolicitudRecurso(self.nombre, recurso, liberar=True)
            self.conexion_solicitudes.put(solicitud)
        self.recursos_asignados = []  # Vaciar la lista de recursos asignados

    # Reduce el tiempo restante del trabajo actual y libera recursos al completarlo
    def ejecutar_job(self):
        # Reducir el tiempo restante del trabajo
        self.estado.current_job.tiempo_completado += 1

        # Si el trabajo se terminó
        if self.estado.current_job.get_tiempo_faltante() <= 0:
            # Liberar recursos asignados
            self.liberar_recursos()                
            # Notificar al maestro que el trabajo se terminó
            self.pipe_trabajos.send((self.nombre, self.estado.current_job.nombre))
            self.estado.current_job = None
            self.estado.activo = False

    # Reporta el estado actual al maestro
    def reportar_estado(self):
        self.conexion_estado.put((self.nombre, self.estado))

    def __recursosSuficientes(self, job: Job):
        for recurso in job.recursos:
            if recurso.nombre not in self.recursos_asignados:
                return False
        return True