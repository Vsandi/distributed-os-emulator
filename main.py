from emulacion import maestro
from lector_script.lector import LectorInstrucciones

def main():
    nodos = ["abc", "xyz"]
    recursos = ["pan", "café", "queque"]
    instrucciones = LectorInstrucciones.leer_instrucciones('instrucciones.txt');
    sistema_maestro = maestro.SistemaMaestro(nodos, recursos, instrucciones, 100, 3)

if __name__ == "__main__":
    main()