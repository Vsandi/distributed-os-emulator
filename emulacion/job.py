from typing import List
from lector_script.instruccion import Instruccion, RecursoInstruccion

class RecursoJob:
    def __init__(self, recurso: RecursoInstruccion):
        self.nombre = recurso.nombre
        self.datos = recurso.datos
        self.tiempo = recurso.tiempo

class Job:
    def __init__(self, instruccion: Instruccion):
        self.nombre = instruccion.nombre
        self.tiempo = instruccion.tiempo
        self.tiempo_completado = 0
        self.recursos = [RecursoJob(recurso) for recurso in instruccion.recursos]
    
    def get_tiempo_faltante(self):
        return self.tiempo - self.tiempo_completado

class RecursoJob:
    def __init__(self, nombre:str, datos:str, tiempo:float, tiempo_utilizado:float):
        self.nombre = nombre
        self.datos = datos
        self.tiempo = tiempo
        self.tiempo_utilizado = tiempo_utilizado