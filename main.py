from emulacion import maestro

# TEMPORAL
from lector_script.instruccion import Instruccion, TipoInstruccion

def main():
    nodos = ["abc", "xyz"]
    recursos = ["pan", "café", "queque"]
    sistema_maestro = maestro.SistemaMaestro(nodos, recursos, 
                                             [
                                                 Instruccion(TipoInstruccion.JOB, "Job 1", 12),
                                                 Instruccion(TipoInstruccion.JOB, "Job 2", 12),
                                                 Instruccion(TipoInstruccion.JOB, "Job 3", 10)
                                              ],
                                               100, 3)

if __name__ == "__main__":
    main()