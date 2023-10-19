#ifndef AURA_COMMONUTIL_H
#define AURA_COMMONUTIL_H

#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/rand.h>
#include <openssl/sha.h>

#define AES_BLOCK_SIZE 16
#define DIGEST_SIZE 32
#define GGM_SIZE 157041
// This is 100% deletion for the highest-volume keyword acc at 0.0001
// Wiki: 314083
// Enron: 1256332
// Crime:157041
#define HASH_SIZE 13

int aes_encrypt(unsigned char *plaintext, int plaintext_len,
                unsigned char *key, unsigned char *iv,
                unsigned char *ciphertext);

int aes_decrypt(unsigned char *ciphertext, int ciphertext_len,
                unsigned char *key, unsigned char *iv,
                unsigned char *plaintext);

void sha256_digest(unsigned char *plaintext, int plaintext_len,
                unsigned char *digest);

unsigned int hmac_digest(unsigned char *plaintext, int plaintext_len,
                 unsigned char *key, int key_len,
                 unsigned char *digest);

unsigned int key_derivation(unsigned char *plaintext, int plaintext_len,
                            unsigned char *key, int key_len,
                            unsigned char *digest);

#endif //AURA_COMMONUTIL_H
