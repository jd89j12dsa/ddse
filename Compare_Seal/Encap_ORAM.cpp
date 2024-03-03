//Create time 2022/5/23
#include <Python.h>
#include <iostream>
#include <string>
#include "OMAP.h"
using namespace std;

map <int,OMAP*> ORAM_instances;

static PyObject* ORAMBatchSetup(PyObject *self , PyObject *args)
{
    PyObject* ret;
    PyObject* datalist;
    int ORAM_number,maxSize;
    map<Bid, string> setupPairs;

    if(!PyArg_ParseTuple(args , "iiO" , &ORAM_number, &maxSize, &datalist))
    {
      return NULL;
    }

    if(!PySequence_Check(datalist))
    {
        PyErr_SetString(PyExc_TypeError, "Expected a list");
        return NULL;
    }

    Py_ssize_t datalen = Py_SIZE(datalist);
    bytes<Key> key1{ORAM_number};
    ORAM_instances[ORAM_number] = new OMAP(maxSize*4, key1);
    
    for (Py_ssize_t i = 0; i<datalen; i++)
    {
        Bid bid(to_string(i));

        PyObject* item = PySequence_GetItem(datalist, i);
        const char* value = PyUnicode_AsUTF8(item);
        setupPairs[bid] = value;
        Py_DECREF(item);
    }

    if (datalen > 0)ORAM_instances[ORAM_number]->batchInsert(setupPairs);

    ret = (PyObject *)Py_BuildValue("i" , 1);
    return ret;
}

static PyObject* ORAMAccess(PyObject *self , PyObject *args)
{
    char *op, *value;
    int ind;
    PyObject* ret;
    int ORAM_number;
    if(!PyArg_ParseTuple(args , "isis", &ORAM_number, &op, &ind, &value))
    {
      return NULL;
    }    

    Bid bid(to_string(ind));
    if (*op == 'r')
    {
        string tmpRes = ORAM_instances[ORAM_number]->find(bid);
        char * p =(char*)tmpRes.data();
        ret = (PyObject* )Py_BuildValue("s", p);
        
    }

    else if (*op == 'w')
    {
        ORAM_instances[ORAM_number]->insert(bid, value);
        ret = (PyObject* )Py_BuildValue("i", 1);        
    }

    return ret;
}


static PyMethodDef
ORAM_methods[] = {
    {"BSetup" , ORAMBatchSetup, METH_VARARGS},
    {"Access", ORAMAccess, METH_VARARGS},
    {0, 0, 0},
};

static struct PyModuleDef
ORAM = {
    PyModuleDef_HEAD_INIT,
    "ORAM",
    "",
    -1,
    ORAM_methods,
    NULL,
    NULL,
    NULL,
    NULL
};


PyMODINIT_FUNC PyInit_ORAM(void)
{
    return PyModule_Create(&ORAM);
}