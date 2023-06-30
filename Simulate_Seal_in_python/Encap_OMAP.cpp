//Create time 2022/5/23
#include <Python.h>
#include <iostream>
#include <string>
#include "OMAP.h"
using namespace std;

map <int,OMAP*> OMAP_instances;

static PyObject* OMAPSetup(PyObject *self , PyObject *args)
{
    PyObject* ret;
    int OMAP_number,maxSize;

    if(!PyArg_ParseTuple(args , "ii" , &OMAP_number, &maxSize))
    {
      return NULL;
    }

    bytes<Key> key1{OMAP_number};
    OMAP_instances[OMAP_number] = new OMAP(maxSize*4, key1);

    ret = (PyObject *)Py_BuildValue("i" , 1);

    return ret;
}


static PyObject* OMAPinsert(PyObject *self , PyObject *args)
{
    PyObject * ret;
    int OMAP_number;
    char * ckeyword;
    char * cvalue;

    if(!PyArg_ParseTuple(args , "iss", &OMAP_number, &ckeyword, &cvalue))
    {
      return NULL;
    }    

    string keyword = ckeyword;
    string value = cvalue;
    Bid bid(keyword);
    OMAP_instances[OMAP_number]->insert(bid, value);

    ret = (PyObject *)Py_BuildValue("i" , 1);

    return ret;
}

static PyObject* OMAPSearch(PyObject *self , PyObject *args)
{
    char * ckeyword;
    PyObject* ret;
    int OMAP_number;
    if(!PyArg_ParseTuple(args , "is", &OMAP_number, &ckeyword))
    {
      return NULL;
    }    

    string keyword = ckeyword;
    Bid bid(keyword);
    string tmpRes = OMAP_instances[OMAP_number]->find(bid);
    char * p =(char*)tmpRes.data();

    ret = (PyObject* )Py_BuildValue("s", p);

    return ret;
}


static PyMethodDef
OMAP_methods[] = {
    {"Setup" , OMAPSetup, METH_VARARGS},
    {"Ins" , OMAPinsert, METH_VARARGS},
    {"Find", OMAPSearch, METH_VARARGS},
    {0, 0, 0},
};

static struct PyModuleDef
OMAP = {
    PyModuleDef_HEAD_INIT,
    "OMAP",
    "",
    -1,
    OMAP_methods,
    NULL,
    NULL,
    NULL,
    NULL
};


PyMODINIT_FUNC PyInit_OMAP(void)
{
    return PyModule_Create(&OMAP);
}