from emulacion import maestro
from lector_script.lector import LectorInstrucciones
from parser.lector_args import LectorArgs

def main():
    args = LectorArgs.parsear_argumentos()
    nodos = args.nodo
    recursos = args.recurso
    timeout = args.timeout
    capacidad_por_nodo = args.capacidad
    instrucciones = LectorInstrucciones.leer_instrucciones(args.path);
    sistema_maestro = maestro.SistemaMaestro(nodos, recursos, instrucciones, timeout, capacidad_por_nodo)

if __name__ == "__main__":
    main()