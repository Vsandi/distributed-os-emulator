from typing import Dict
from rich.table import Table

class Logger:
    def generar_tabla(nodos: Dict[str, any]):
        table = Table(title="Logger", expand=True)

        table.add_column("Nodo", style="cyan")
        table.add_column("Estado", style="yellow")
        table.add_column("Job", style="magenta")
        table.add_column("Progreso", style="green")
        table.add_column("Recursos", style="dark_blue")

        for nombre, nodo in nodos.items():
            job = nodo.get_trabajo_actual()
            if job is not None:
                progress_percentage = ((job.tiempo_completado/job.tiempo)*100)
                nombres_recursos = []
                for recurso in job.recursos:
                    nombres_recursos.append(recurso.nombre)
                recursos = ", ".join(nombres_recursos)
                table.add_row(
                    nombre,
                    "Activo",
                    job.nombre,
                    f"{progress_percentage:.2f}%",
                    recursos
                )
            else:
                table.add_row(
                    nombre,
                    "Inactivo",
                    "...",
                    "...",
                    "..."
                )

        return table