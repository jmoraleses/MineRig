import numpy as np
import pyopencl as cl
import pyopencl as cl


def calculate_sha256_nonce(header, target, num_device):
    # Cargar el contenido del archivo sha256.cl
    with open("sha256.cl", "r") as f:
        kernel_code = f.read()

    # Crear el contexto y la cola de comandos
    platform = cl.get_platforms()[0]
    device = platform.get_devices()[num_device]
    context = cl.Context([device])
    queue = cl.CommandQueue(context)

    # Compilar el kernel
    program = cl.Program(context, kernel_code).build()

    # target_bytes = bytes.fromhex(target)

    # Crear un buffer para los datos en la memoria del dispositivo
    header_buffer = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=header)
    toRet_buffer = cl.Buffer(context, cl.mem_flags.WRITE_ONLY, size=32)
    target_buffer = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=target)

    # Ejecutar el kernel
    num_keys = 1  # Solo estamos calculando un hash
    program.Sha256_1(queue, (num_keys,), None, header_buffer, toRet_buffer, target_buffer)

    # Transferir el resultado de vuelta a la CPU
    toRet = np.zeros(32, dtype=np.uint8)
    cl.enqueue_copy(queue, toRet, toRet_buffer)

    nonce_hex = ''.join(format(toRet[j], '02x') for j in range(4))
    version_hex = ''.join(format(toRet[j + 4], '02x') for j in range(4))

    header_buffer.release()
    toRet_buffer.release()

    return nonce_hex, version_hex
