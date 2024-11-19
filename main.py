import asyncio
from sistema.sistema import SistemaMaestro, EstadoSistema, Recurso

async def main():
    estado_sistema = EstadoSistema()
    sistema_maestro = SistemaMaestro("Maestro", estado_sistema)

if __name__ == "__main__":
    asyncio.run(main())