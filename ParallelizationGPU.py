import hashlib
import pyopencl as cl
import numpy as np


def calculate_sha256_nonce(header):
    # Cargar el contenido del archivo sha256.cl
    with open("sha256.cl", "r") as f:
        kernel_code = f.read()

    # Crear el contexto y la cola de comandos
    platform = cl.get_platforms()[0]
    device = platform.get_devices()[0]
    context = cl.Context([device])
    queue = cl.CommandQueue(context)

    # Compilar el kernel
    program = cl.Program(context, kernel_code).build()

    # Crear un buffer para los datos en la memoria del dispositivo
    header_buffer = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=header)
    toRet_buffer = cl.Buffer(context, cl.mem_flags.WRITE_ONLY, size=32)

    # Ejecutar el kernel
    num_keys = 1  # Solo estamos calculando un hash
    program.Sha256_1(queue, (num_keys,), None, header_buffer, toRet_buffer)

    # Transferir el resultado de vuelta a la CPU
    toRet = np.zeros(32, dtype=np.uint8)
    cl.enqueue_copy(queue, toRet, toRet_buffer)

    # Convertir el resultado a formato hexadecimal
    nonce_hex = ''.join(format(toRet[j], '02x') for j in range(32))

    # Liberar recursos
    header_buffer.release()
    toRet_buffer.release()

    return nonce_hex[::-1]

#
# if __name__ == "__main__":
#     header = np.zeros(80, dtype=np.uint8)  # Aquí debes colocar tus datos de cabecera
#     calculated_nonce = calculate_sha256_nonce(header)
#
#     reference_nonce = hashlib.sha256(hashlib.sha256(header).digest()).hexdigest()[::-1]
#
#     print("Calculated Nonce:", calculated_nonce)
#     print("Reference Nonce:", reference_nonce)
#
#     if calculated_nonce == reference_nonce:
#         print("Nonces match!")
#     else:
#         print("Nonces do not match!")
