from emulacion import maestro

def main():
    nodos = ["abc", "xyz"]
    recursos = ["pan", "café", "queque"]
    sistema_maestro = maestro.SistemaMaestro(nodos, recursos, [], 10, 3)

if __name__ == "__main__":
    main()