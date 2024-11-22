from multiprocessing import Array, Value
from ctypes import c_char, c_int

class Recurso:
    def __init__(self, nombre:str):
        self.nombre = nombre
        self.len = Value(c_int, lock=False)
        self.len.value = 0
        self.data = Array(c_char, 256, lock=False)

class SolicitudRecurso:
    def __init__(self, nodo:str, recurso:str, liberar=False):
        self.nodo = nodo
        self.recurso = recurso
        self.liberar = liberar