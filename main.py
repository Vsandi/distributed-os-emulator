from emulacion import maestro

def main():
    nodos = ["abc", "xyz"]
    recursos = ["pan", "café", "queque"]
    sistema_maestro = maestro.SistemaMaestro(nodos, recursos, [])

if __name__ == "__main__":
    main()