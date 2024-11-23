from typing import List
from enum import Enum

class TipoInstruccion(Enum):
    JOB = 1
    NUEVONODO = 2
    DESCONECTAR = 3
    TIMEOUT = 4

class RecursoInstruccion:
    def __init__(self, nombre: str, datos: str):
        self.nombre = nombre
        self.datos = datos

class Instruccion:
    recursos: List[RecursoInstruccion]
    def __init__(self, tipo: TipoInstruccion, nombre: str, tiempo: int):
        self.tipo = tipo
        self.nombre = nombre
        self.tiempo = tiempo
        self.recursos = []