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

class Sistema:
    def __init__(self, nombre:str, recursos:List[Recurso], pipe_trabajos:connection,
                cola_reportes_maestro:connection, conexion_solicitudes:connection):
        self.nombre = nombre
        self.estado = EstadoSistema()
        self.recursos = recursos
        self.pipe_trabajos = pipe_trabajos 
        self.cola_reportes_maestro = cola_reportes_maestro
        self.conexion_solicitudes = conexion_solicitudes
    
    def reportar_estado(self):
        print(f"Estado del sistema '{self.nombre}': {self.estado}")
    
    def solicitar_recurso(self, nombre_recurso:str):
        # Crear una solicitud de recurso para este nodo
        solicitud = SolicitudRecurso(self.nombre, nombre_recurso)
        
        # Verificar si el recurso está disponible y procesa la solicitud
        recurso = next((r for r in self.recursos if r.nombre == nombre_recurso), None)
        if recurso:
            if recurso.len.value == 0:
                # Si el recurso está libre
                recurso.len.value = 1  # Marcar el recurso como ocupado
                print(f"{self.nombre} ha solicitado y obtenido el recurso {nombre_recurso}")
            else:
                # Si el recurso ya está ocupado
                print(f"{self.nombre} no pudo obtener el recurso {nombre_recurso}, está ocupado.")
        else:
            print(f"Recurso {recurso} no encontrado.")

    def liberar_recurso(self, nombre_recurso:str):
        recurso = next((r for r in self.recursos if r.nombre == nombre_recurso), None)
        if recurso:
            recurso.len.value = 0  # Marcar el recurso como libre
            print(f"{self.nombre} ha liberado el recurso {nombre_recurso}")
        else:
            print(f"Recurso {nombre_recurso} no encontrado.")