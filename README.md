# MineRig

### Programa de minería con rigs en la nube

StratumPool.py: Esta clase es la clase de la ejecución principal del programa, facilita la comunicación con el servidor de minería y realiza la minería de bloques utilizando el protocolo Stratum.

ParallelizationGPU.py: Aporta paralelización en la GPU con pyopencl.

BlockTemplateFetcher.py: Se utiliza para obtener información sobre el bloque actual conectándose a Bitcoin Core (debe estar instalado y ejecutándose).

Config.py: Almacena información como la dirección del servidor de minería, el puerto, las credenciales de autenticación, etc.

StratumProcessing.py: Contiene todos los métodos necesarios para el preprocesamiento, realizar cálculos relacionados con la minería, así como el cálculo del hash del bloque para su validación.

SimulateRig: Contiene una versión simple y pequeña de una conexión cliente-servidor.
