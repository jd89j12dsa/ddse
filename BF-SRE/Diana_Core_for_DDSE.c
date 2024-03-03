#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/sha.h>
#include <openssl/hmac.h>
#include <openssl/aes.h>
#define SHA512_LEN 64
#define LOOP_CONSTRAIN 1
#define	RET_SUCCESS 1
#define MAX_KEY_DEPTH 20
#define AES_BLOCK_SIZE 16

static unsigned char owner_key[AES_BLOCK_SIZE]={0};
static unsigned char key_left[AES_BLOCK_SIZE]={0};
static unsigned char key_right[AES_BLOCK_SIZE]={0};

static void _xor(unsigned char* a , unsigned char* b ,unsigned int len , unsigned char* c)
{
    for(int i =0 ; i< len ; i++)c[i] = a[i]^b[i];
        return;
}

int CPRF_eval (unsigned char *session_key , unsigned int key_len , unsigned int key_depth , 
	unsigned int input  , unsigned char* output_key , unsigned int* output_len)
{

	unsigned int original_key_depth = key_depth;
	unsigned int test_int = 1<<key_depth;
	unsigned char  reduction_key[SHA512_LEN]={0};

	memcpy(reduction_key , session_key , key_len);

	while(key_depth > 0)
	{
		test_int = test_int >> 1 ;
		key_depth--;
		if( (test_int & input) > 0 )
			my_aes_encrypt(reduction_key, reduction_key , key_len, key_right );

		else
			my_aes_encrypt(reduction_key,reduction_key,key_len,key_left);
	}

	//printf("CPRF_eval caculate times %d\n" , original_key_depth-key_depth);
	memcpy(output_key , reduction_key , key_len);
	*output_len = key_len;

	return RET_SUCCESS;
}
int CPRF_constrain (unsigned char *main_key , unsigned int main_key_len , unsigned int cnt,  
	unsigned char * session_key ,unsigned int * session_key_len ,  unsigned int * key_depth)
{
	unsigned int max_key_depth = MAX_KEY_DEPTH;
	unsigned int test_int = 1 << max_key_depth;
	unsigned int test_key_depth = max_key_depth;
	unsigned char reduction_key[SHA512_LEN]={0};

	memcpy(reduction_key , main_key , main_key_len);

	while(test_key_depth > 0 )
	{
		test_int = test_int >> 1;
		test_key_depth -- ;

		if((test_int & cnt)==0)
			my_aes_encrypt(reduction_key ,reduction_key , main_key_len , key_left);
		else
		{
			test_key_depth ++ ; 
			break;
		}
	}

	memcpy(session_key , reduction_key , main_key_len);
	//printf("CPRF_constrain times %d\n" , max_key_depth - test_key_depth);

	*key_depth = test_key_depth;
	*session_key_len = main_key_len;

	return RET_SUCCESS;
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

static PyObject* Setup(PyObject *self , PyObject *args)
{
    PyObject * ret;

	clock_t t_start,t_end;
	t_start = clock();

    RAND_pseudo_bytes(owner_key,AES_BLOCK_SIZE);
    RAND_pseudo_bytes(key_left,AES_BLOCK_SIZE);
    RAND_pseudo_bytes(key_right,AES_BLOCK_SIZE);

	t_end = clock();
    double dur = (double)(t_end-t_start);

    ret = (PyObject *)Py_BuildValue("dy#y#y#" , dur/CLOCKS_PER_SEC,owner_key,AES_BLOCK_SIZE,
    	key_left,AES_BLOCK_SIZE,
    	key_right,AES_BLOCK_SIZE
    	);

    return ret;
}

static PyObject* Continue(PyObject *self , PyObject *args)
{
	PyObject *ret;
	unsigned char* ok; unsigned int owner_key_len;
	unsigned char* kl; unsigned int key_left_len;
	unsigned char* kr; unsigned int key_right_len;
	 if(!PyArg_ParseTuple(args , "y#y#y#" , &ok, &owner_key_len, &kl, &key_left_len,&kr ,&key_right_len))
    {
      return NULL;
    }

    memcpy(owner_key,ok,AES_BLOCK_SIZE);
    memcpy(key_left,kl,AES_BLOCK_SIZE);
    memcpy(key_right,kr,AES_BLOCK_SIZE);

    ret = (PyObject *)Py_BuildValue("i",1);

    return ret; 
}

static PyObject* Encrypt(PyObject *self , PyObject *args)
{
    PyObject *ret;
    unsigned char k_w1[EVP_MAX_MD_SIZE]={0}; unsigned int k_w1_len;
    unsigned char k_w2[EVP_MAX_MD_SIZE]={0}; unsigned int k_w2_len;


    unsigned char ct_1[EVP_MAX_MD_SIZE] = {0}; unsigned int ct_1_len;

 
    unsigned char keyword_cnt_eval[EVP_MAX_MD_SIZE] = {0} ; unsigned int keyword_cnt_eval_len;

    unsigned char fileid_bytes[EVP_MAX_MD_SIZE] = {0};
    unsigned char keyword_bytes[EVP_MAX_MD_SIZE] = {0};
    unsigned char keyword_bytes_cipher[EVP_MAX_MD_SIZE] = {0};

    unsigned char *keyword;
    unsigned int keyword_cnt;

    if(!PyArg_ParseTuple(args , "si" , &keyword, &keyword_cnt))
    {
      return NULL;
    }

    clock_t t_start,t_end;
	t_start = clock();

		HMAC(EVP_sha256(),owner_key,AES_BLOCK_SIZE, keyword,strlen(keyword) ,k_w1 , &k_w1_len);
		HMAC(EVP_sha256(),owner_key,AES_BLOCK_SIZE, k_w1,k_w1_len ,k_w2 , &k_w2_len);

		CPRF_eval(k_w1 , k_w1_len , MAX_KEY_DEPTH , keyword_cnt , keyword_cnt_eval , &keyword_cnt_eval_len);
		//ct1
		HMAC(EVP_sha256(),k_w2 , k_w2_len , keyword_cnt_eval , keyword_cnt_eval_len , ct_1 , &ct_1_len);
		

	t_end = clock();
    double dur = (double)(t_end-t_start);

    ret = (PyObject* )Py_BuildValue("dy#" , dur/CLOCKS_PER_SEC , 
    	 ct_1 , ct_1_len
	);

    return ret;
}

static PyObject* Xor (PyObject *self , PyObject *args)
{
	PyObject *ret;
	unsigned char *in1 , *in2; 
	unsigned int in1_len , in2_len;
	unsigned char out[EVP_MAX_MD_SIZE]={0}; unsigned int out_len;

	if(!PyArg_ParseTuple(args , "y#y#" , &in1 ,&in1_len ,&in2 , &in2_len))
    {
      return NULL;
    }

    _xor(in1 , in2 , in1_len , out);
    out_len = in1_len;

   	ret = (PyObject *)Py_BuildValue("y#" , out , out_len);

   	return ret;
}
static PyObject* Trapdoor(PyObject *self , PyObject *args)
{
    PyObject *ret;

    unsigned char *keyword;
	unsigned int keyword_cnt;
	unsigned int key_depth;
	unsigned char k_w1[EVP_MAX_MD_SIZE]={0}; unsigned int k_w1_len;
    unsigned char k_w2[EVP_MAX_MD_SIZE]={0}; unsigned int k_w2_len;
    unsigned char k_w1_constrain[EVP_MAX_MD_SIZE] = {0}; unsigned int k_w1_constrain_len;
    unsigned int k_w1_constrain_depth;

    if(!PyArg_ParseTuple(args , "si" , &keyword ,  &keyword_cnt))
    {
      return NULL;
    }

    HMAC(EVP_sha256(),owner_key,AES_BLOCK_SIZE, keyword,strlen(keyword) ,k_w1 , &k_w1_len);
	HMAC(EVP_sha256(),owner_key,AES_BLOCK_SIZE, k_w1,k_w1_len ,k_w2 , &k_w2_len);

    clock_t t_start,t_end;
	t_start = clock();

	CPRF_constrain(k_w1,k_w1_len,keyword_cnt,k_w1_constrain, &k_w1_constrain_len, &k_w1_constrain_depth);

	t_end = clock();
    double dur = (double)(t_end-t_start);

    ret = (PyObject* )Py_BuildValue("dy#y#i" , dur/CLOCKS_PER_SEC , 
    	k_w2 , k_w2_len, 
    	k_w1_constrain , k_w1_constrain_len,
    	k_w1_constrain_depth);

    return ret;
}

static PyObject* Search(PyObject *self , PyObject *args)
{
    PyObject *ret;
    unsigned char *k_w2; unsigned int k_w2_len;
    unsigned char *k_w1_constrain; unsigned int k_w1_constrain_len;
    unsigned char keyword_cnt_eval[EVP_MAX_MD_SIZE] = {0}; unsigned int keyword_cnt_eval_len;
    unsigned char ct_1[EVP_MAX_MD_SIZE] = {0} ; unsigned int ct_1_len;
    unsigned int keyword_cnt;
    unsigned int k_w1_constrain_depth;
	if(!PyArg_ParseTuple(args , "iy#y#i" , &keyword_cnt,&k_w2, &k_w2_len,
		&k_w1_constrain ,&k_w1_constrain_len, &k_w1_constrain_depth ))
    {
      return NULL;
    }

    clock_t t_start,t_end;
	t_start = clock();

	CPRF_eval(k_w1_constrain , k_w1_constrain_len , k_w1_constrain_depth , 
			keyword_cnt , keyword_cnt_eval , &keyword_cnt_eval_len);
		/*debug code */
		/*
		if(memcmp(ReEncrypt_keyword_eval,keyword_cnt_eval,k_w1_constrain_len)!=0)
		{
			printf("false in CPRF_eval\n");
		}
		*/
		HMAC(EVP_sha256(),k_w2 , k_w2_len , keyword_cnt_eval 
			, keyword_cnt_eval_len , ct_1 , &ct_1_len);

	t_end = clock();
    double dur = (double)(t_end-t_start);	
	ret = (PyObject *)Py_BuildValue("dy#" , dur/CLOCKS_PER_SEC,
		ct_1,ct_1_len);

    return ret;
}


static PyMethodDef
Diana_methods[] = {
    {"Setup" , Setup, METH_VARARGS},
    {"Encrypt" , Encrypt , METH_VARARGS},
    {"Trapdoor" , Trapdoor, METH_VARARGS},
    {"Search" , Search,METH_VARARGS},
    {"Continue", Continue,METH_VARARGS},
    {"Xor",Xor,METH_VARARGS},
    {0, 0, 0},
};

static struct PyModuleDef
Diana = {
    PyModuleDef_HEAD_INIT,
    "Diana",
    "",
    -1,
    Diana_methods,
    NULL,
    NULL,
    NULL,
    NULL
};


PyMODINIT_FUNC PyInit_Diana(void)
{
    return PyModule_Create(&Diana);
}