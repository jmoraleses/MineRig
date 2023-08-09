# MineRig

*** Actualmente en desarrollo ***

### Programa de minería con rigs en la nube


BlockTemplateFetcher.py: Se utiliza para obtener información sobre el bloque actual conectándose a Bitcoin Core (debe estar instalado y ejecutándose).

Config.py: Almacena información como la dirección del servidor de minería, el puerto, las credenciales de autenticación, etc.

StratumClient.py: Esta clase representa un cliente Stratum, que es un protocolo utilizado para la comunicación entre los mineros y los servidores de minería. Implementa la lógica para establecer una conexión con el servidor, enviar y recibir mensajes Stratum, y procesar las respuestas del servidor.

StratumMessage.py: Para Serializar y Deserializar mensajes json.

StratumPool.py: Esta clase es la clase de la ejecución principal del programa, facilita la comunicación con el servidor de minería y realiza la minería de bloques utilizando el protocolo Stratum.

StratumProcessing.py: Contiene todos los métodos necesarios para el preprocesamiento, realizar cálculos relacionados con la minería, así como el cálculo del hash del bloque para su validación.

SimulateRig: Contiene una versión simple y pequeña de una conexión cliente-servidor.
