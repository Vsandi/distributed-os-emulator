from typing import List, Dict
import time
import multiprocessing
from rich.console import Console
from rich.live import Live
from logger.logger import Logger
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
        self.trabajo_actual = None
        self.carga_asignada = 0
        self.tiempo_sin_conexion = 0
        self.recursos = []

    def set_estado(self, estado: EstadoSistema):
        self.tiempo_sin_conexion = 0
        self.carga_asignada = estado.get_carga()
        if estado.cola_procesos is not None:
            self.trabajos_asignados = list(estado.cola_procesos)
        if estado.current_job is not None:
            self.trabajos_asignados.append(estado.current_job)
            self.trabajo_actual = estado.current_job
        else:
            self.trabajos_asignados = []

    def get_trabajo_actual(self) -> Job:
        return self.trabajo_actual

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

        # Registro Jobs Asignados: Backup ante fallos de sistemas
        self.procesos_asignados: Dict[str, Job] = {nodo: [] for nodo in nodos}

        # Registro de Jobs sin Asignar
        self.cola_procesos_sin_asignar = []

        # Inicializar Nodos
        self.nodos: Dict[str, Nodo] = {}
        for nodo in nodos:
            self.agregar_nodo(nodo)

        self.administrar(instrucciones, timeout)

        
    def administrar(self, instrucciones, timeout):
        # Rich console
        consola = Console()

        # Contador para timeouts: 
        # En 0 lee instrucciones del script
        # Else: Administra pero no lee instrucciones, bajando 1 por segundo el counter
        timeout_counter = 0
        index_instrucciones = 0


        # Game Loop
        with Live(Logger.generar_tabla(self.nodos), refresh_per_second=1, console=consola, transient=True) as live:
            while True:
                # Manejar Instrucciones Hasta Timeout
                if (timeout_counter == 0):
                    while index_instrucciones < len(instrucciones):
                        if instrucciones[index_instrucciones].tipo == instruccion.TipoInstruccion.TIMEOUT:
                            timeout_counter = instrucciones[index_instrucciones].tiempo
                            index_instrucciones += 1
                            break
                        elif instrucciones[index_instrucciones].tipo == instruccion.TipoInstruccion.NUEVONODO:
                            self.agregar_nodo(instrucciones[index_instrucciones].nombre)
                        elif instrucciones[index_instrucciones].tipo == instruccion.TipoInstruccion.DESCONECTAR:
                            self.eliminar_nodo(instrucciones[index_instrucciones].nombre)
                        elif instrucciones[index_instrucciones].tipo == instruccion.TipoInstruccion.JOB:
                            self.cola_procesos_sin_asignar.append(Job(instrucciones[index_instrucciones]))
                        index_instrucciones += 1

                # Reportar Estado
                live.update(Logger.generar_tabla(self.nodos))

                # Manejar llegada de estados
                while not self.conexion_estado.empty():
                    nombre, estado = self.conexion_estado.get()
                    if nombre in self.nodos:
                        self.nodos[nombre].set_estado(estado)

                # Asignar Trabajos Segun Carga
                while self.numero_jobs_actuales() < self.capacidad_maxima and len(self.cola_procesos_sin_asignar) != 0:
                    job = self.cola_procesos_sin_asignar.pop()
                    self.asignar_job(job)

                # Manejar solicitudes recursos
                while not self.cola_solicitudes_recursos.empty():
                    solicitud = self.cola_solicitudes_recursos.get()
                    self.manejar_solicitud_recurso(solicitud)

                # Revisar jobs
                for nodo in self.nodos.values():
                    if nodo.pipe_trabajos.poll():
                        nombre, job = nodo.pipe_trabajos.recv()
                        self.finalizar_job(nombre, job)
                        
                # Revisar Final de Loop
                if len(self.cola_procesos_sin_asignar) == 0 and self.numero_jobs_actuales() == 0 and timeout_counter == 0:
                    break

                time.sleep(1)
                for nombre, nodo in self.nodos.items():
                    nodo.tiempo_sin_conexion += 1
                    if nodo.tiempo_sin_conexion >= timeout:
                        self.eliminar_nodo(nombre)
                if len(self.nodos) == 0:
                    break
                timeout_counter = max(0, timeout_counter-1)

        # Epilogo
        consola.print("Todos los trabajos han sido completados! Saliendo de la emulacion...", style="bold green")
        # Print Recursos Content...
        for nodo in list(self.nodos):
            self.eliminar_nodo(nodo)
    
    def agregar_nodo(self, nombre:str):
        conexion_maestro, conexion_nodo = multiprocessing.Pipe()
        cola_recursos_asignados = multiprocessing.Queue()
        nuevo_proceso = multiprocessing.Process(target=Sistema, args=[nombre, self.recursos, conexion_nodo, self.conexion_estado, self.cola_solicitudes_recursos, cola_recursos_asignados])
        self.nodos[nombre] = Nodo(nuevo_proceso, conexion_maestro, cola_recursos_asignados)
        self.procesos_asignados[nombre] = []
        self.capacidad_maxima = len(self.nodos) * self.capacidad_por_nodo
        nuevo_proceso.start()

    def eliminar_nodo(self, nombre:str):
        # Pasar jobs a la cola de procesos sin asignar
        self.cola_procesos_sin_asignar.extend(self.procesos_asignados[nombre])
        # Terminar Proceso
        self.nodos[nombre].proceso.terminate()
        # Marcar recursos como disponible
        for recurso in self.nodos[nombre].recursos:
            self.locks_recursos[recurso] = False
        # Eliminar nodo de los nodos
        self.nodos.pop(nombre)
        # Eliminar nodo de los procesos asignados
        self.procesos_asignados.pop(nombre)

    def manejar_solicitud_recurso(self, solicitud:SolicitudRecurso):
        if solicitud.liberar: # Si es para liberar, se libera
            self.nodos[solicitud.nodo].recursos.remove(solicitud.recurso)
            self.locks_recursos[solicitud.recurso] = False
            return
        elif self.locks_recursos[solicitud.recurso]: # Si se ocupa, se revisa que no este ocupado
            return
        
        # Marcar como ocupado
        self.locks_recursos[solicitud.recurso] = True
        self.nodos[solicitud.nodo].cola_recursos_asignados.put(solicitud.recurso)
        self.nodos[solicitud.nodo].recursos.append(solicitud.recurso)


    def asignar_job(self, job: Job):
        nodo_con_menor_carga: Nodo = None
        nombre_nodo_con_menor_carga = None
        for nombre, nodo in self.nodos.items():
            if len(self.procesos_asignados[nombre]) == 0:
                nodo.pipe_trabajos.send(job)
                self.procesos_asignados[nombre].append(job)
                nodo.trabajos_asignados.append(job)
                return
            
            if nodo_con_menor_carga == None or nodo_con_menor_carga.carga_asignada > nodo.carga_asignada:
                nodo_con_menor_carga = nodo
                nombre_nodo_con_menor_carga = nombre

        self.procesos_asignados[nombre_nodo_con_menor_carga].append(job)
        nodo_con_menor_carga.pipe_trabajos.send(job)
        nodo_con_menor_carga.trabajos_asignados.append(job)


    def finalizar_job(self, nodo: str, job: str):
        self.nodos[nodo].trabajo_actual = None
        for trabajo in self.procesos_asignados[nodo]:
            if trabajo.nombre == job:
                self.procesos_asignados[nodo].remove(trabajo)
        for trabajo in self.nodos[nodo].trabajos_asignados:
            if trabajo.nombre == job:
                self.nodos[nodo].trabajos_asignados.remove(trabajo)
            
    def numero_jobs_actuales(self):
        contador = 0
        for trabajos in self.procesos_asignados.values():
            contador += len(trabajos)
        return contador