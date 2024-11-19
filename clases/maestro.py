from clases.sistema import EstadoSistema, Sistema
from typing import List
from multiprocessing import connection
from clases.nodo import Nodo
from clases.recurso import Recurso, SolicitudRecurso

class SistemaMaestro(Sistema):
    def __init__(self, nombre:str, recursos:List[Recurso], pipe_trabajos:connection,
                cola_reportes_maestro:connection, conexion_solicitudes:connection, conexion_recursos:connection,
                instrucciones:str, nodos:List[Nodo], conexion_estado:connection):
        super().__init__(nombre, recursos, pipe_trabajos, cola_reportes_maestro, conexion_solicitudes, conexion_recursos)
        self.nodos = nodos
        self.conexion_estado = conexion_estado
        self.cola_solicitudes_recursos
        self.estados
        self.locks_recursos
        self.cola_procesos_sin_asignar
        # TODO: implementar lógica de las instrucciones
    
    def agregar_nodo(nombre:str):
        # TODO: implementar lógica
        pass

    def manejar_solicitud_recurso(solicitud:SolicitudRecurso):
        # TODO: implementar lógica
        pass