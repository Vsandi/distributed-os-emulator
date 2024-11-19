from multiprocessing import Array

class Recurso:
    def __init__(self, nombre:str):
        self.nombre = nombre
        self.data = Array('c', 255, lock=False)

class SolicitudRecurso:
    def __init__(self, nodo:str, recurso:str):
        self.nodo = nodo
        self.recurso = recurso