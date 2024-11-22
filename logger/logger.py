from typing import Dict
from rich.table import Table
# from emulacion.maestro import Nodo

class Logger:
    def generar_tabla(nodos: Dict[str, any]):
        table = Table(title="Logger", expand=True)

        table.add_column("Nodo", style="cyan", no_wrap=True)
        table.add_column("Estado", style="yellow")
        table.add_column("Job", style="magenta")
        table.add_column("Progreso", style="green")

        for nombre, nodo in nodos.items():
            job = nodo.get_trabajo_actual()
            if job is not None:
                progress_percentage = ((job.tiempo_completado/job.tiempo)*100)
                table.add_row(
                    nombre,
                    "Activo",
                    job.nombre,
                    f"{progress_percentage:.2f}%"
                )
            else:
                table.add_row(
                    nombre,
                    "Inactivo",
                    "",
                    f"{0:.2f}%"
                )

        return table