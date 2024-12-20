import time
from lector_script.instruccion import Instruccion, TipoInstruccion, RecursoInstruccion
from typing import List

class LectorInstrucciones:
    def leer_instrucciones(archivo:str):
        instrucciones = []
        with open(archivo, "r") as file:
            lineas = file.readlines()

        for linea in lineas:
            linea = linea.strip()
            partes = linea.split()

            tipo = TipoInstruccion[partes[0].upper()]
            nombre = partes[1] 
            tiempo = None 
            if (tipo == TipoInstruccion.TIMEOUT):
                tiempo = int(partes[1])
            elif (tipo == TipoInstruccion.JOB):
                tiempo = int(partes[2])

            instruccion = Instruccion(tipo, nombre, tiempo)
            for i in range(3, len(partes), 3):
                if partes[i] == "--recurso":
                    nombre_recurso = partes[i + 1]
                    datos = partes[i + 2]
                    recurso = RecursoInstruccion(nombre_recurso, datos)
                    instruccion.recursos.append(recurso)

            instrucciones.append(instruccion)
        return instrucciones