import argparse

class LectorArgs:
    def parsear_argumentos():
        parseador = argparse.ArgumentParser(
            description="Emulador Distribuido para Procesamiento en Nodos con Recursos"
        )
        # Requeridos
        parseador.add_argument(
            "path", type=str, help="Path al archivo de instrucciones."
        )
        parseador.add_argument(
            "timeout", type=int, help="Timeout en segundos."
        )
        parseador.add_argument(
            "capacidad", type=int, help="Capacidad maxima de trabajos por nodo."
        )
        # Optional, multiple arguments
        parseador.add_argument(
            "--nodo", action="append", required=True, help="Nombre del nodo. Puede repetirse para multiples nodos."
        )
        parseador.add_argument(
            "--recurso", action="append", required=False, help="Nombre del recurso. Puede repetirse para multiples recursos."
        )
        return parseador.parse_args()