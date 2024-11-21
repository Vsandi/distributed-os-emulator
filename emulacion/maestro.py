from typing import List
import time
import multiprocessing
from emulacion.recurso import Recurso, SolicitudRecurso
from emulacion.job import Job
from lector_script import instruccion

class Nodo:
    def __init__(self, nombre:str, queue_aviso_recurso:multiprocessing.connection, 
                pipe_trabajos:multiprocessing.connection, trabajos_asignados:float, carga_asignada:float):
        self.queue_aviso_recurso = queue_aviso_recurso
        self.pipe_trabajos = pipe_trabajos
        self.trabajos_asignados = trabajos_asignados
        self.carga_asignada = carga_asignada
        self.tiempo_sin_conexion = 0

class SistemaMaestro():
    def __init__(self, nodos:List[str], recursos:List[str], instrucciones:List[instruccion.Instruccion], timeout:int):
        
        # Inicializar Cola de Solicitud de Recursos
        self.cola_solicitudes_recursos = multiprocessing.Queue()

        # Inicializar Conexion para transmitir estado servidor
        self.conexion_estado = multiprocessing.Queue()
        
        # Inicializar Recursos
        self.recursos = [Recurso(recurso) for recurso in recursos]
        self.locks_recursos = {recurso: False for recurso in recursos}

        # Inicializar Nodos
        self.nodos = {}
        for nodo in nodos:
            self.agregar_nodo(nodo)

        self.cola_procesos_sin_asignar = []
        
        timeout_counter = 0

        while True:
            # Manejar Instrucciones Hasta Timeout
            if (timeout_counter == 0):
                for inst in instrucciones:
                    if inst.tipo == instruccion.TipoInstruccion.TIMEOUT:
                        timeout_counter = inst.tiempo
                        break
                    elif inst.tipo == instruccion.TipoInstruccion.NEW:
                        self.agregar_nodo(inst.nombre)
                    elif inst.tipo == instruccion.TipoInstruccion.DISCONNECT:
                        self.eliminar_nodo(inst.nombre)
                    elif inst.tipo == instruccion.TipoInstruccion.JOB:
                        self.cola_procesos_sin_asignar.append(Job(inst))
            
            while len(self.cola_procesos_sin_asignar) != 0:
                pass

            # Manejar llegada de estados
            while not self.conexion_estado.empty():
                nombre, estado = self.conexion_estado.get()
                self.nodos[nombre].tiempo_sin_conexion = 0

            for nombre in self.nodos:
                self.nodos[nombre].tiempo_sin_conexion += 1
                if self.nodos[nombre].tiempo_sin_conexion == timeout:
                    self.eliminar_nodo(nombre)

            # Manejar solicitudes recursos
            while not self.cola_solicitudes_recursos:
                solicitud = self.cola_solicitudes_recursos.get()
                self.manejar_solicitud_recurso(solicitud)

            # Revisar jobs

            time.sleep(1)
            timeout_counter = max(0, timeout_counter-1)

    
    def agregar_nodo(self, nombre:str):
        # TODO: implementar lógica
        pass

    def eliminar_nodo(self, nombre:str):
        # TODO: implementar lógica
        pass

    def manejar_solicitud_recurso(solicitud:SolicitudRecurso):
        # TODO: implementar lógica
        pass

    def asignar_job(job: Job):
        # TODO: implementar logica
        pass