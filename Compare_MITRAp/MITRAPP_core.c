//Create time 2022/5/23
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/sha.h>
#include <openssl/hmac.h>
#include <openssl/aes.h>
#define SHA512_LEN 64
#define SHA256_SIZE 32
#define LOOP_CONSTRAIN 1
#define	RET_SUCCESS 1
#define AES_BLOCK_SIZE 16


static PyObject* PRF(PyObject *self , PyObject *args)
{
    PyObject * ret;
 	unsigned char* key; unsigned int key_len;
 	unsigned char* input; unsigned int input_len;
 	unsigned char output[SHA256_SIZE] = {0}; unsigned int output_len;

 	if(!PyArg_ParseTuple(args , "y#s" , &key, &key_len,&input))
    {
      return NULL;
    }

    input_len = strlen(input);
    clock_t t_start,t_end;
	t_start = clock();

    HMAC(EVP_sha256(),key,key_len, input,input_len ,output , &output_len);

	t_end = clock();
    double dur = (double)(t_end-t_start);	
	ret = (PyObject *)Py_BuildValue("dy#" , dur/CLOCKS_PER_SEC,
		output,output_len);

    return ret;
}

int my_aes_encrypt(unsigned char *in , unsigned char *out , size_t len , unsigned char* key)
{

	if(!in||!key||!out)
	{
		printf("%s\n" , "invaid input");
		return -1;
	}

	unsigned char iv[AES_BLOCK_SIZE];
	memset(iv , 0 , AES_BLOCK_SIZE);

	AES_KEY aes;

	if(AES_set_encrypt_key((unsigned char*)key , 128 , &aes) < 0)
	{
		perror("AES_set_encrypt_key()");
		return 0;
	}

	AES_cbc_encrypt((unsigned char*)in , (unsigned char*)out , len , &aes , iv , AES_ENCRYPT);

	return len;
}
int my_aes_decrypt(unsigned char *in , unsigned char *out , size_t len  , unsigned char* key)
{
	if(!in||!key||!out)
	{

		return -1;
	}

	unsigned char iv[AES_BLOCK_SIZE];
	memset(iv , 0 , AES_BLOCK_SIZE);

	AES_KEY aes;
	if(AES_set_decrypt_key((unsigned char*)key , 128 , &aes) < 0)
	{
		perror("AES_set_decrypt_key()");
		return 0;
	}
	AES_cbc_encrypt((unsigned char*)in , (unsigned char*)out , len , &aes , iv , AES_DECRYPT);

	return len;
}
static PyObject* AESDecrypt(PyObject *self , PyObject *args)
{
	PyObject * ret;
	unsigned int key_len, cipher_len,plain_len;
	unsigned char *cipher, *key;
	unsigned char plaintext[300]={0};
	if(!PyArg_ParseTuple(args , "y#y#" , &key, &key_len , &cipher, &cipher_len ))
    {
      return NULL;
    }

    clock_t t_start,t_end;
	t_start = clock();

	plain_len = my_aes_decrypt(cipher,plaintext,cipher_len,key);
	while (*(plaintext+plain_len-1)=='$')plain_len--;


	t_end = clock();
    double dur = (double)(t_end-t_start);
 
    ret = (PyObject* )Py_BuildValue("ds#",dur/CLOCKS_PER_SEC,
    	 plaintext, plain_len
    	 );

    return ret;
}

static PyObject* AESEncrypt(PyObject *self , PyObject *args)
{
	PyObject * ret;
	unsigned int key_len, plaintext_len;
	unsigned char *plaintext, *key;
	unsigned char cipher[300]={0};
	unsigned char mask[300]={0};
	unsigned int cipherlen,masklen;
	if(!PyArg_ParseTuple(args , "y#s#" , &key, &key_len , &plaintext, &plaintext_len ))
    {
      return NULL;
    }

    clock_t t_start,t_end;
	t_start = clock();

	memset(mask,'$',300);
	memcpy(mask,plaintext,plaintext_len);

	masklen = plaintext_len;
    if (plaintext_len%16 != 0) masklen = ((plaintext_len/16)+1)*16;

	cipherlen = my_aes_encrypt(mask,cipher,masklen,key);

	t_end = clock();
    double dur = (double)(t_end-t_start);
 
    ret = (PyObject* )Py_BuildValue("dy#",dur/CLOCKS_PER_SEC,
    	 cipher, cipherlen
    	 );

    return ret;
}

static PyMethodDef
MITRAPP_methods[] = {
    {"PRF" , PRF, METH_VARARGS},
    {"AESEncrypt", AESEncrypt, METH_VARARGS},
    {"AESDecrypt", AESDecrypt, METH_VARARGS},
    {0, 0, 0},
};

static struct PyModuleDef
MITRAPP = {
    PyModuleDef_HEAD_INIT,
    "MITRAPP",
    "",
    -1,
    MITRAPP_methods,
    NULL,
    NULL,
    NULL,
    NULL
};


PyMODINIT_FUNC PyInit_MITRAPP(void)
{
    return PyModule_Create(&MITRAPP);
}