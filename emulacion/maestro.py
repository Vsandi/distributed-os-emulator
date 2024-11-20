from typing import List
import multiprocessing
from emulacion.recurso import Recurso, SolicitudRecurso
from lector_script import instruccion

class Nodo:
    def __init__(self, nombre:str, queue_aviso_recurso:multiprocessing.connection, 
                pipe_trabajos:multiprocessing.connection, trabajos_asignados:float, carga_asignada:float):
        self.nombre = nombre
        self.queue_aviso_recurso = queue_aviso_recurso
        self.pipe_trabajos = pipe_trabajos
        self.trabajos_asignados = trabajos_asignados
        self.carga_asignada = carga_asignada

class SistemaMaestro():
    def __init__(self, nodos:List[str], recursos:List[str], instrucciones:List[instruccion.Instruccion]):
        
        # Inicializar Cola de Solicitud de Recursos
        self.cola_solicitudes_recursos = multiprocessing.Queue()

        # Inicializar Conexion para transmitir estado servidor
        self.conexion_estado = multiprocessing.Queue()
        
        # Inicializar Recursos
        self.recursos = [Recurso(recurso) for recurso in recursos]
        self.locks_recursos = {recurso: False for recurso in recursos}

        # Inicializar Nodos
        self.nodos = []
        self.estados = {}
        for nodo in nodos:
            self.agregar_nodo(nodo)
        self.cola_procesos_sin_asignar = []
        
        for instruccion in instrucciones:
            # TODO: Implementar loop de instrucciones
            pass
    
    def agregar_nodo(self, nombre:str):
        # TODO: implementar lógica
        pass

    def manejar_solicitud_recurso(solicitud:SolicitudRecurso):
        # TODO: implementar lógica
        pass