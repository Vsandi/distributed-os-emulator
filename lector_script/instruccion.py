from typing import List
from enum import Enum

class TipoInstruccion(Enum):
    JOB = 1
    NEW = 2
    DISCONNECT = 3
    TIMEOUT = 4

class RecursoInstruccion:
    def __init__(self, nombre: str, datos: str, tiempo: int):
        self.nombre = nombre
        self.datos = datos
        self.tiempo = tiempo

class FalloInstruccion:
    def __init__(self, tiempo, tiempo_recuperacion):
        self.tiempo = tiempo
        self.tiempo_recuperacion = tiempo_recuperacion

class Instruccion:
    recursos: List[RecursoInstruccion]
    fallos: List[FalloInstruccion]
    def __init__(self, tipo: TipoInstruccion, nombre: str, tiempo: int):
        self.tipo = tipo
        self.nombre = nombre
        self.tiempo = tiempo
        self.recursos = []
        self.fallos = []