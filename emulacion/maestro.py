from typing import List, Dict
import time
import multiprocessing
from emulacion.sistema import Sistema, EstadoSistema
from emulacion.recurso import Recurso, SolicitudRecurso
from emulacion.job import Job
from lector_script import instruccion

class Nodo:
    def __init__(self, proceso: multiprocessing.Process,
                pipe_trabajos:multiprocessing.connection, cola_recursos_asignados: multiprocessing.Queue):
        self.proceso = proceso
        self.pipe_trabajos = pipe_trabajos
        self.cola_recursos_asignados = cola_recursos_asignados
        self.trabajos_asignados = []
        self.carga_asignada = 0
        self.tiempo_sin_conexion = 0
        self.recursos = []

    def set_estado(self, estado: EstadoSistema):
        self.tiempo_sin_conexion = 0
        self.carga_asignada = estado.get_carga()
        self.trabajos_asignados = estado.cola_procesos.append(estado.current_job)

class SistemaMaestro():
    def __init__(self, nodos:List[str], recursos:List[str], instrucciones:List[instruccion.Instruccion], timeout:int, capacidad_por_nodo:int):
        # Setear capacidad por nodo
        self.capacidad_por_nodo = capacidad_por_nodo        
        # Setear numero maximo de trabajos del sistema
        self.capacidad_maxima = len(nodos) * capacidad_por_nodo

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

        self.administrar(instrucciones, timeout)

        
    def administrar(self, instrucciones, timeout):
        # Contador para timeouts: 
        # En 0 lee instrucciones del script
        # Else: Administra pero no lee instrucciones, bajando 1 por segundo el counter
        timeout_counter = 0

        # Game Loop
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

            # Reportar Estado


            # Manejar llegada de estados
            while not self.conexion_estado.empty():
                nombre, estado = self.conexion_estado.get()
                self.nodos[nombre].set_estado(estado)

            # Asignar Trabajos Segun Carga
            while self.numero_jobs_actuales() < self.capacidad_maxima and len(self.cola_procesos_sin_asignar) != 0:
                self.asignar_job(self.cola_procesos_sin_asignar.pop(0))

            # Manejar solicitudes recursos
            while not self.cola_solicitudes_recursos.empty():
                solicitud = self.cola_solicitudes_recursos.get()
                self.manejar_solicitud_recurso(solicitud)

            # Revisar jobs
            for nodo in self.nodos.values():
                if nodo.pipe_trabajos.poll():
                    job = nodo.pipe_trabajos.recv()
                    self.finalizar_job(job)
                    
            # Revisar Final de Loop
            if len(self.cola_procesos_sin_asignar) == 0:
                procesos_terminados = True
                for nodo in self.nodos.values():
                    if len(nodo.trabajos_asignados) != 0:
                        procesos_terminados = False
                        break
                if procesos_terminados:
                    break
                

            time.sleep(1)
            for nombre, nodo in self.nodos.items():
                nodo.tiempo_sin_conexion += 1
                if nodo.tiempo_sin_conexion == timeout:
                    self.eliminar_nodo(nombre)
            if len(self.nodos) == 0:
                break
            timeout_counter = max(0, timeout_counter-1)

        # Epilogo

    
    def agregar_nodo(self, nombre:str):
        conexion_maestro, conexion_nodo = multiprocessing.Pipe()
        cola_recursos_asignados = multiprocessing.Queue()
        nuevo_proceso = multiprocessing.Process(target=Sistema, args=[nombre, self.recursos, conexion_nodo, self.conexion_estado, self.cola_solicitudes_recursos, cola_recursos_asignados])
        self.nodos[nombre] = Nodo(nuevo_proceso, conexion_maestro, cola_recursos_asignados)
        self.capacidad_maxima = len(self.nodos) * self.capacidad_por_nodo
        nuevo_proceso.start()

    def eliminar_nodo(self, nombre:str):
        # Terminar Proceso
        self.nodos[nombre].proceso.terminate()
        # Marcar recursos como disponible
        for recurso in self.nodos[nombre].recursos:
            self.locks_recursos[recurso.nombre] = False
        # Eliminar nodo de los nodos
        self.nodos.pop(nombre)
        # Pasar jobs a la cola de procesos sin asignar
        self.cola_procesos_sin_asignar.extend(self.procesos_asignados[nombre])
        # Eliminar nodo de los procesos asignados
        self.procesos_asignados.pop(nombre)

    def manejar_solicitud_recurso(self, solicitud:SolicitudRecurso):
        if solicitud.liberar: # Si es para liberar, se libera
            self.nodos[solicitud.nodo].recursos.pop(solicitud.recurso)
            self.locks_recursos[solicitud.recurso] = False
        elif self.locks_recursos[solicitud.recurso]: # Si se ocupa, se revisa que no este ocupado
            return
        
        # Marcar como ocupado
        self.locks_recursos[solicitud.recurso] = True
        self.nodos[solicitud.nodo].cola_recursos_asignados.put(solicitud.recurso)


    def asignar_job(self, job: Job):
        nodo_con_menor_carga: Nodo = None
        nombre_nodo_con_menor_carga = None
        for nombre, nodo in self.nodos.items():
            if nodo.carga_asignada == 0:
                nodo.pipe_trabajos(job)
                self.procesos_asignados[nombre].append(job)
                return
            
            if nodo_con_menor_carga.carga_asignada > nodo.carga_asignada:
                nombre_nodo_con_menor_carga = nombre
                nodo_con_menor_carga = nodo

        self.procesos_asignados[nombre].append(job)
        nodo_con_menor_carga.pipe_trabajos(job)


    def finalizar_job(self, nodo: str, job: str):
        for job_asignado in self.procesos_asignados[nodo]:
            if job_asignado.nombre == job:
                self.procesos_asignados[nodo].remove(job_asignado)
                return
            
    def numero_jobs_actuales(self):
        contador = 0
        for nodo in self.nodos.values():
            contador += len(nodo.trabajos_asignados)
        return contador