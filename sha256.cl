  #ifndef uint8_t
 #define uint8_t  unsigned char
 #endif

 #ifndef uint32_t
 #define uint32_t unsigned int
 #endif
 #ifndef uint64_t
 #define uint64_t unsigned long int
 #endif
 #define rotlFixed(x, n) (((x) << (n)) | ((x) >> (32 - (n))))
#define rotrFixed(x, n) (((x) >> (n)) | ((x) << (32 - (n))))

#define SHA256_DIGEST_LENGTH 32

typedef struct
{
  uint32_t state[8];
  uint64_t count;
  uint8_t buffer[64];
} CSha256;

inline void Sha256_Init(CSha256 *p)
{
  p->state[0] = 0x6a09e667;
  p->state[1] = 0xbb67ae85;
  p->state[2] = 0x3c6ef372;
  p->state[3] = 0xa54ff53a;
  p->state[4] = 0x510e527f;
  p->state[5] = 0x9b05688c;
  p->state[6] = 0x1f83d9ab;
  p->state[7] = 0x5be0cd19;
  p->count = 0;
}

#define S0(x) (rotrFixed(x, 2) ^ rotrFixed(x,13) ^ rotrFixed(x, 22))
#define S1(x) (rotrFixed(x, 6) ^ rotrFixed(x,11) ^ rotrFixed(x, 25))
#define s0(x) (rotrFixed(x, 7) ^ rotrFixed(x,18) ^ (x >> 3))
#define s1(x) (rotrFixed(x,17) ^ rotrFixed(x,19) ^ (x >> 10))

#define blk0(i) (W[i] = data[i])
#define blk2(i) (W[i&15] += s1(W[(i-2)&15]) + W[(i-7)&15] + s0(W[(i-15)&15]))

#define Ch2(x,y,z) (z^(x&(y^z)))
#define Maj(x,y,z) ((x&y)|(z&(x|y)))

#define sha_a(i) T[(0-(i))&7]
#define sha_b(i) T[(1-(i))&7]
#define sha_c(i) T[(2-(i))&7]
#define sha_d(i) T[(3-(i))&7]
#define sha_e(i) T[(4-(i))&7]
#define sha_f(i) T[(5-(i))&7]
#define sha_g(i) T[(6-(i))&7]
#define sha_h(i) T[(7-(i))&7]


#ifdef _SHA256_UNROLL2

#define R(a,b,c,d,e,f,g,h, i) h += S1(e) + Ch2(e,f,g) + K[i+j] + (j?blk2(i):blk0(i));\
  d += h; h += S0(a) + Maj(a, b, c)

#define RX_8(i) \
  R(a,b,c,d,e,f,g,h, i); \
  R(h,a,b,c,d,e,f,g, i+1); \
  R(g,h,a,b,c,d,e,f, i+2); \
  R(f,g,h,a,b,c,d,e, i+3); \
  R(e,f,g,h,a,b,c,d, i+4); \
  R(d,e,f,g,h,a,b,c, i+5); \
  R(c,d,e,f,g,h,a,b, i+6); \
  R(b,c,d,e,f,g,h,a, i+7)

#else

#define R(i) sha_h(i) += S1(sha_e(i)) + Ch2(sha_e(i),sha_f(i),sha_g(i)) + K[i+j] + (j?blk2(i):blk0(i));\
  sha_d(i) += sha_h(i); sha_h(i) += S0(sha_a(i)) + Maj(sha_a(i), sha_b(i), sha_c(i))

#ifdef _SHA256_UNROLL

#define RX_8(i) R(i+0); R(i+1); R(i+2); R(i+3); R(i+4); R(i+5); R(i+6); R(i+7);

#endif

#endif

static const uint32_t K[64] = {
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
  0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
  0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
  0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
  0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
  0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
  0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
  0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
  0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

inline static void Sha256_Transform(uint32_t *state, const uint32_t *data)
{
  uint32_t W[16];
  unsigned j;
  #ifdef _SHA256_UNROLL2
  uint32_t a,b,c,d,e,f,g,h;
  a = state[0];
  b = state[1];
  c = state[2];
  d = state[3];
  e = state[4];
  f = state[5];
  g = state[6];
  h = state[7];
  #else
  uint32_t T[8];
  for (j = 0; j < 8; j++)
    T[j] = state[j];
  #endif

  for (j = 0; j < 64; j += 16)
  {
    #if defined(_SHA256_UNROLL) || defined(_SHA256_UNROLL2)
    RX_8(0); RX_8(8);
    #else
    unsigned i;
    for (i = 0; i < 16; i++) { R(i); }
    #endif
  }

  #ifdef _SHA256_UNROLL2
  state[0] += a;
  state[1] += b;
  state[2] += c;
  state[3] += d;
  state[4] += e;
  state[5] += f;
  state[6] += g;
  state[7] += h;
  #else
  for (j = 0; j < 8; j++)
    state[j] += T[j];
  #endif

  /* Wipe variables */
  /* memset(W, 0, sizeof(W)); */
  /* memset(T, 0, sizeof(T)); */
}

#undef S0
#undef S1
#undef s0
#undef s1

inline static void Sha256_WriteByteBlock(CSha256 *p)
{
  uint32_t data32[16];
  unsigned i;
  for (i = 0; i < 16; i++)
    data32[i] =
      ((uint32_t)(p->buffer[i * 4    ]) << 24) +
      ((uint32_t)(p->buffer[i * 4 + 1]) << 16) +
      ((uint32_t)(p->buffer[i * 4 + 2]) <<  8) +
      ((uint32_t)(p->buffer[i * 4 + 3]));
  Sha256_Transform(p->state, data32);
}

inline void Sha256_Update(CSha256 *p, __global const uint8_t *data, size_t size)
{
  uint32_t curBufferPos = (uint32_t)p->count & 0x3F;
  while (size > 0)
  {
    p->buffer[curBufferPos++] = *data++;
    p->count++;
    size--;
    if (curBufferPos == 64)
    {
      curBufferPos = 0;
      Sha256_WriteByteBlock(p);
    }
  }
}

inline void Sha256_Final(CSha256 *p, __global uint8_t *digest)
{
  uint64_t lenInBits = (p->count << 3);
  uint32_t curBufferPos = (uint32_t)p->count & 0x3F;
  unsigned i;
  p->buffer[curBufferPos++] = 0x80;
  while (curBufferPos != (64 - 8))
  {
    curBufferPos &= 0x3F;
    if (curBufferPos == 0)
      Sha256_WriteByteBlock(p);
    p->buffer[curBufferPos++] = 0;
  }
  for (i = 0; i < 8; i++)
  {
    p->buffer[curBufferPos++] = (uint8_t)(lenInBits >> 56);
    lenInBits <<= 8;
  }
  Sha256_WriteByteBlock(p);

  for (i = 0; i < 8; i++)
  {
    *digest++ = (uint8_t)(p->state[i] >> 24);
    *digest++ = (uint8_t)(p->state[i] >> 16);
    *digest++ = (uint8_t)(p->state[i] >> 8);
    *digest++ = (uint8_t)(p->state[i]);
  }
  Sha256_Init(p);
}


inline void Sha256_Update1(CSha256 *p, const uint8_t *data, uint32_t size)
{
  uint32_t curBufferPos = (uint32_t)p->count & 0x3F;
  while (size > 0)
  {
    p->buffer[curBufferPos++] = *data++;
    p->count++;
    size--;
    if (curBufferPos == 64)
    {
      curBufferPos = 0;
      Sha256_WriteByteBlock(p);
    }
  }
}

inline void Sha256_Final1(CSha256 *p, uint8_t *digest)
{
  uint64_t lenInBits = (p->count << 3);
  uint32_t curBufferPos = (uint32_t)p->count & 0x3F;
  unsigned i;
  p->buffer[curBufferPos++] = 0x80;
  while (curBufferPos != (64 - 8))
  {
    curBufferPos &= 0x3F;
    if (curBufferPos == 0)
      Sha256_WriteByteBlock(p);
    p->buffer[curBufferPos++] = 0;
  }
  for (i = 0; i < 8; i++)
  {
    p->buffer[curBufferPos++] = (uint8_t)(lenInBits >> 56);
    lenInBits <<= 8;
  }
  Sha256_WriteByteBlock(p);

  for (i = 0; i < 8; i++)
  {
    *digest++ = (uint8_t)(p->state[i] >> 24);
    *digest++ = (uint8_t)(p->state[i] >> 16);
    *digest++ = (uint8_t)(p->state[i] >> 8);
    *digest++ = (uint8_t)(p->state[i]);
  }
  Sha256_Init(p);
}


__kernel void __Sha256_1(__global uint8_t *header, __global uint8_t *toRet)
{
    uint8_t tempHdr[80];
    uint8_t tempDigest[32] = {0};

    for (int x = 0; x < 80; x++)
        tempHdr[x] = header[x];

    CSha256 p;
    Sha256_Init(&p);
    Sha256_Update1(&p, tempHdr, 80);
    Sha256_Final1(&p, tempDigest);

    CSha256 p1;
    Sha256_Init(&p1);
    Sha256_Update1(&p1, tempDigest, 32);
    Sha256_Final1(&p1, tempDigest);

    for (int x = 0; x < 32; x++)
    {
        toRet[x] = tempDigest[x];
    }
}


uint32_t bytesToUint32(const uchar *bytes) {
    return (uint32_t)(bytes[0] << 24) | (uint32_t)(bytes[1] << 16) | (uint32_t)(bytes[2] << 8) | (uint32_t)bytes[3];
}


__kernel void Sha256_1(__global uint8_t *header, __global uint8_t *toRet, __global uint8_t *targetBytes)
{
    uint8_t tempHdr[80];
    uint8_t tempDigest[32] = {0};
    uint32_t nonce = 0; // Inicio del rango de nonce: 0
    bool hashFound = false; // Bandera para controlar la terminación de los bucles

    // Copiar el encabezado al búfer temporal
    for (int x = 0; x < 80; x++)
        tempHdr[x] = header[x];

    CSha256 p;
    CSha256 p1;

    uint32_t target = (uint32_t)(targetBytes[9] << 24) | (uint32_t)(targetBytes[10] << 16) | (uint32_t)(targetBytes[11] << 8) | (uint32_t)targetBytes[12];
    int target_integer = (int)target;

    // Buscar un nonce válido
    while (nonce <= 4294967295 && !hashFound)
    {
        // Actualizar el nonce en el encabezado
        for (int i = 0; i < 8; i++) {
            tempHdr[72 + i] = (nonce >> (8 * i)) & 0xFF;
        }

        // Calcular el primer hash SHA-256
        Sha256_Init(&p);
        Sha256_Update1(&p, tempHdr, 80);
        Sha256_Final1(&p, tempDigest);

        // Calcular el segundo hash SHA-256
        Sha256_Init(&p1);
        Sha256_Update1(&p1, tempDigest, 32);
        Sha256_Final1(&p1, tempDigest);

        // Convertir el hash a un valor uint32_t para compararlo con el objetivo
        // uint32_t hashValue = (tempDigest[31] << 24) | (tempDigest[30] << 16) | (tempDigest[29] << 8) | tempDigest[28];
        // uint64_t hashValue = 0;

        // for (int i = 0; i < 4; i++) {
        //     hashValue |= ((uint64_t)tempDigest[i] << (8 * (3 - i)));
        // }

        // printf("%llu\n%llu\n", target_integer, hashValue);

        // Comprobar si los últimos 19 bytes del hashValue son ceros
        bool hasLast19Zeroes = false;

        for (int i = 4; i < 8; i++) {
            if ((tempDigest[i] >> (8 * (7 - i))) & 0xFF) {
                hasLast19Zeroes = true;
                break;
            }
        }

        // Comprobar si el hash cumple la condición del objetivo
        if (hasLast19Zeroes)
        {
            // Almacenar el valor completo del nonce en el búfer de salida
            for (int i = 0; i < 8; i++) {
                toRet[i] = (nonce >> (8 * (7 - i))) & 0xFF;
            }

            //printf("%llu\n", toRet);

            // Establecer la bandera para salir de los bucles
            hashFound = true;
            break; // Salir del bucle interior
        }

        nonce = nonce + 1; // Incrementar el nonce para la siguiente iteración
    }

    // Restaurar el valor de nonce
    nonce = 0;
}




void hash256(__global uchar* input, __global uchar* output) {
    uint8_t tempHdr[80];
    uint8_t tempDigest[32] = {0};

    // Copiar el encabezado al búfer temporal
    for (int x = 0; x < 80; x++)
        tempHdr[x] = input[x];

    CSha256 p;
    CSha256 p1;

    // Calcular el primer hash SHA-256
    Sha256_Init(&p);
    Sha256_Update1(&p, tempHdr, 80);
    Sha256_Final1(&p, tempDigest);

    // Calcular el segundo hash SHA-256
    Sha256_Init(&p1);
    Sha256_Update1(&p1, tempDigest, 32);
    Sha256_Final1(&p1, tempDigest);

    // Almacenar el resultado en el búfer de salida
    for (int i = 0; i < 32; i++)
        output[i] = tempDigest[i];
}


__kernel void concatExtranonce(__global const char *input, __global char *results, ulong total_combinations, uint start_position) {
    size_t gid = get_global_id(0);
    ulong extranonce = gid + start_position;
    ulong final_extranonce = total_combinations + start_position;

    while (extranonce < final_extranonce) {
        for (int i = 0; i < 76; ++i) {
            results[gid * 80 + i] = input[start_position + i];
        }
        for (int i = 0; i < 4; ++i) {
            results[gid * 80 + 76 + i] = (extranonce >> (8 * i)) & 0xFF;
        }

        gid += get_global_size(0);  // Avanzar al siguiente bloque
        extranonce = gid + start_position;
    }
}

