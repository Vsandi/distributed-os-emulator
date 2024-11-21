from typing import List, Dict
import time
import multiprocessing
from emulacion.sistema import EstadoSistema
from emulacion.recurso import Recurso, SolicitudRecurso
from emulacion.job import Job
from lector_script import instruccion

class Nodo:
    def __init__(self, nombre:str, queue_aviso_recurso:multiprocessing.connection, 
                pipe_trabajos:multiprocessing.connection):
        self.queue_aviso_recurso = queue_aviso_recurso
        self.pipe_trabajos = pipe_trabajos
        self.trabajos_asignados = []
        self.carga_asignada = 0
        self.tiempo_sin_conexion = 0

    def set_estado(self, estado: EstadoSistema):
        self.carga_asignada = estado.get_carga()
        self.trabajos_asignados = estado.cola_procesos.append(estado.current_job)

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
        self.nodos: Dict[str, Nodo] = {}
        for nodo in nodos:
            self.agregar_nodo(nodo)

        # Registro de Jobs sin Asignar
        self.cola_procesos_sin_asignar = []

        # Registro Jobs Asignados: Backup ante fallos de sistemas
        self.procesos_asignados = {nodo: [] for nodo in nodo}

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
            
            # Asignar Trabajos Segun Carga
            while len(self.cola_procesos_sin_asignar) != 0:
                self.asignar_job(self.cola_procesos_sin_asignar.pop())

            # Manejar llegada de estados
            while not self.conexion_estado.empty():
                nombre, estado = self.conexion_estado.get()
                self.nodos[nombre].tiempo_sin_conexion = 0
                self.nodos[nombre].set_estado(estado)

            # Manejar solicitudes recursos
            while not self.cola_solicitudes_recursos:
                solicitud = self.cola_solicitudes_recursos.get()
                self.manejar_solicitud_recurso(solicitud)

            # Revisar jobs
            for nodo in nodos:
                if self.nodos[nombre].pipe_trabajos.poll():
                    job = self.nodos[nombre].pipe_trabajos.recv()
                    self.finalizar_job(job)
                    
            # TODO Revisar final del loop 


            time.sleep(1)
            for nombre in nodos:
                self.nodos[nombre].tiempo_sin_conexion += 1
                if self.nodos[nombre].tiempo_sin_conexion == timeout:
                    self.eliminar_nodo(nombre)
            timeout_counter = max(0, timeout_counter-1)

        # Epilogo

    
    def agregar_nodo(self, nombre:str):
        # TODO: implementar lógica
        pass

    def eliminar_nodo(self, nombre:str):
        # TODO: implementar lógica
        pass

    def manejar_solicitud_recurso(self, solicitud:SolicitudRecurso):
        # TODO: implementar lógica
        pass

    def asignar_job(self, job: Job):
        # TODO: implementar logica
        pass

    def finalizar_job(self, nodo: str, job: str):
        for job_asignado in self.procesos_asignados[nodo]:
            if job_asignado.nombre == job:
                self.procesos_asignados[nodo].remove(job_asignado)
                return