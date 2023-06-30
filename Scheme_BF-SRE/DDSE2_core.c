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


static unsigned char Ks[AES_BLOCK_SIZE]={0};
static unsigned char Kt[AES_BLOCK_SIZE]={0};
static unsigned char Kc[AES_BLOCK_SIZE]={0};


static PyObject* Setup(PyObject *self , PyObject *args)
{
    PyObject * ret;

	clock_t t_start,t_end;
	t_start = clock();

    RAND_pseudo_bytes(Ks,AES_BLOCK_SIZE);
    RAND_pseudo_bytes(Kt,AES_BLOCK_SIZE);
    RAND_pseudo_bytes(Kc,AES_BLOCK_SIZE);

	t_end = clock();
    double dur = (double)(t_end-t_start);

    ret = (PyObject *)Py_BuildValue("dy#y#y#" , dur/CLOCKS_PER_SEC,Ks,AES_BLOCK_SIZE,
    	Kt,AES_BLOCK_SIZE,
    	Kc,AES_BLOCK_SIZE
    	);

    return ret;
}

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

static void _xor(unsigned char* a , unsigned char* b ,unsigned int len , unsigned char* c)
{
    for(int i =0 ; i< len ; i++)c[i] = a[i]^b[i];
        return;
}

static PyObject* Xor (PyObject *self , PyObject *args)
{
    PyObject *ret;
    unsigned char *in1 , *in2; 
    unsigned int in1_len , in2_len;
    unsigned char out[EVP_MAX_MD_SIZE]={0}; unsigned int out_len;
    unsigned char inte1[EVP_MAX_MD_SIZE] ={0};
    unsigned char inte2[EVP_MAX_MD_SIZE] ={0};

    if(!PyArg_ParseTuple(args , "y#y#" , &in1 ,&in1_len ,&in2 , &in2_len))
    {
      return NULL;
    }

    memcpy(inte1, in1, in1_len);
    memcpy(inte2, in2, in2_len);
    _xor(inte1 , inte2 , EVP_MAX_MD_SIZE , out);
    out_len = EVP_MAX_MD_SIZE;

    ret = (PyObject *)Py_BuildValue("y#" , out , out_len);

    return ret;
}

static PyMethodDef
DDSE2_methods[] = {
    {"PRF" , PRF, METH_VARARGS},
    {"Xor" , Xor, METH_VARARGS},
    {"Setup", Setup, METH_VARARGS},
    {0, 0, 0},
};

static struct PyModuleDef
DDSE2 = {
    PyModuleDef_HEAD_INIT,
    "DDSE2",
    "",
    -1,
    DDSE2_methods,
    NULL,
    NULL,
    NULL,
    NULL
};


PyMODINIT_FUNC PyInit_DDSE2(void)
{
    return PyModule_Create(&DDSE2);
}