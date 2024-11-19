from multiprocessing import connection

class Nodo:
    def __init__(self, nombre:str, queue_aviso_recurso:connection, 
                pipe_trabajos:connection, trabajos_asignados:float, carga_asignada:float):
        self.nombre = nombre
        self.queue_aviso_recurso = queue_aviso_recurso
        self.pipe_trabajos = pipe_trabajos
        self.trabajos_asignados = trabajos_asignados
        self.carga_asignada = carga_asignada