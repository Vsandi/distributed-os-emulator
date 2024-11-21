from typing import List
from emulacion.fail import Fail
from lector_script.instruccion import Instruccion, RecursoInstruccion, FalloInstruccion

class RecursoJob:
    def __init__(self, recurso: RecursoInstruccion):
        self.nombre = recurso.nombre
        self.datos = recurso.datos
        self.tiempo = recurso.tiempo
        self.tiempo_utilizado = 0

class FalloJob:
    def __init__(self, fallo:FalloInstruccion):
        self.tiempo = fallo.tiempo
        self.tiempo_recuperacion = fallo.tiempo_recuperacion

class Job:
    def __init__(self, instruccion: Instruccion):
        self.nombre = instruccion.nombre
        self.tiempo = instruccion.tiempo
        self.recursos = [RecursoJob(recurso) for recurso in instruccion.recursos]
        self.recursos = [FalloJob(fallo) for fallo in instruccion.fallos]
    
    def get_tiempo_faltante():
        # TODO: implementar lógica, retorna number
        pass

class RecursoJob:
    def __init__(self, nombre:str, datos:str, tiempo:float, tiempo_utilizado:float):
        self.nombre = nombre
        self.datos = datos
        self.tiempo = tiempo
        self.tiempo_utilizado = tiempo_utilizado