from typing import List
from emulacion.fail import Fail

class Job:
    def __init__(self, nombre:str, tiempo:float, recursos:List[str], fails:List[Fail], tiempo_completado:float):
        self.nombre = nombre    
        self.tiempo = tiempo
        self.recursos = recursos
        self.fails = fails
        self.tiempo_completado = tiempo_completado
    
    def get_tiempo_faltante():
        # TODO: implementar lógica, retorna number
        pass

class RecursoJob:
    def __init__(self, nombre:str, datos:str, tiempo:float, tiempo_utilizado:float):
        self.nombre = nombre
        self.datos = datos
        self.tiempo = tiempo
        self.tiempo_utilizado = tiempo_utilizado