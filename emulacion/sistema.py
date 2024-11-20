from emulacion.job import Job
from emulacion.recurso import Recurso
from typing import List
from multiprocessing import connection

class EstadoSistema:
    def __init__(self, activo:bool, current_job:Job, 
                cola_procesos:list[Job], disconnected_time:float):
        self.activo = activo
        self.current_job = current_job
        self.cola_procesos = cola_procesos
        self.disconnected_time = disconnected_time
    
    def get_carga():
        # TODO: implementar lógica, retorna number
        pass

class Sistema:
    def __init__(self, nombre:str, recursos:List[Recurso], pipe_trabajos:connection,
                cola_reportes_maestro:connection, conexion_solicitudes:connection, conexion_recursos:connection):
        self.nombre = nombre
        self.estado = EstadoSistema()
        self.recursos = recursos
        self.pipe_trabajos = pipe_trabajos 
        self.cola_reportes_maestro = cola_reportes_maestro
        self.conexion_solicitudes = conexion_solicitudes
        self.conexion_recursos = conexion_recursos
    
    def reportar_estado(self):
        print(f"Estado del sistema '{self.nombre}': {self.estado}")
    
    def solicitar_recurso(self, recurso:str):
        # TODO: implementar lógica
        pass

    def liberar_recurso(self, recurso:str):
        # TODO: implementar lógica
        pass