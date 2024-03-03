#include <Python.h>
#include <iostream>
#include <string>
#include <cstring>
#include <map>
#include "SRE_Encap.h"
using namespace std;

map <int, SRE_Encap*> sre_ins;

PyObject* convertVectorIntToPython(const std::vector<int>& vec) {
    PyObject* pyList = PyList_New(vec.size());
    for (size_t i = 0; i < vec.size(); ++i) {
        PyObject* pyInt = PyLong_FromLong(vec[i]);
        PyList_SetItem(pyList, i, pyInt);
    }
    return pyList;
}


PyObject* convertDataPairToPython(const DataPair& dataPair) {

    PyObject* pyCiphertextList = PyList_New(dataPair.ciphertext_list.size());
    for (size_t i = 0; i < dataPair.ciphertext_list.size(); ++i) {
        const std::string& binaryStr = dataPair.ciphertext_list[i];
        PyObject* pyBinaryStr = Py_BuildValue("y#", binaryStr.data(), binaryStr.size());
        PyList_SetItem(pyCiphertextList, i, pyBinaryStr);
    }

    PyObject* pyDataPair = Py_BuildValue("y#O", dataPair.tagString, DIGEST_SIZE, pyCiphertextList);

    // Don't forget to decref intermediate objects to avoid memory leaks
    Py_DECREF(pyCiphertextList);

    return pyDataPair;
}

// Function to convert GGMNode to Python object
PyObject* convertGGMNodeToPython(const GGMNode& node) {
    PyObject* pyIndex = PyLong_FromLong(node.index);
    PyObject* pyLevel = PyLong_FromLong(node.level);
    PyObject* pyKey = Py_BuildValue("y#", node.key, AES_BLOCK_SIZE);

    PyObject* pyGGMNode = Py_BuildValue("OOO", pyIndex, pyLevel, pyKey);

    // Don't forget to decref intermediate objects to avoid memory leaks
    Py_DECREF(pyIndex);
    Py_DECREF(pyLevel);
    Py_DECREF(pyKey);

    return pyGGMNode;
}


// Function to convert DataKrev to Python object
PyObject* convertDataKrevToPython(const DataKrev& dataKrev) {
    PyObject* pyNodeList = PyList_New(dataKrev.node_list.size());
    for (size_t i = 0; i < dataKrev.node_list.size(); ++i) {
        PyObject* pyNode = convertGGMNodeToPython(dataKrev.node_list[i]);
        PyList_SetItem(pyNodeList, i, pyNode);
    }

    PyObject* pyLevel = PyLong_FromLong(dataKrev.level);

    PyObject* pyDataKrev = Py_BuildValue("OO", pyNodeList, pyLevel);

    // Don't forget to decref intermediate objects to avoid memory leaks
    Py_DECREF(pyNodeList);
    Py_DECREF(pyLevel);

    return pyDataKrev;
}


// Function to convert Python object to GGMNode
bool convertPythonToGGMNode(PyObject* pyNode, GGMNode& node) {
    if (!PyTuple_Check(pyNode) || PyTuple_Size(pyNode) != 3) {
        PyErr_SetString(PyExc_TypeError, "Invalid GGMNode format");
        return false;
    }

    PyObject* pyIndexObj = PyTuple_GetItem(pyNode, 0);
    PyObject* pyLevelObj = PyTuple_GetItem(pyNode, 1);
    PyObject* pyKeyObj = PyTuple_GetItem(pyNode, 2);

    if (!PyLong_Check(pyIndexObj) || !PyLong_Check(pyLevelObj) || !PyBytes_Check(pyKeyObj)) {
        PyErr_SetString(PyExc_TypeError, "Invalid GGMNode format");
        return false;
    }

    node.index = PyLong_AsLong(pyIndexObj);
    node.level = PyLong_AsLong(pyLevelObj);
    // Cast node.key to char* before passing to PyBytes_AsStringAndSize
    Py_ssize_t keySize;
    char* keyBytes;
    if (PyBytes_AsStringAndSize(pyKeyObj, &keyBytes, &keySize) < 0) {
        PyErr_SetString(PyExc_TypeError, "Invalid GGMNode key format");
        return false;
    }

    if (keySize != AES_BLOCK_SIZE) {
        PyErr_SetString(PyExc_TypeError, "Invalid GGMNode key size");
        return false;
    }

    memcpy(node.key, keyBytes, AES_BLOCK_SIZE);

    // for(int i = 0; i< AES_BLOCK_SIZE; i++)node.key[i]=0;

    return true;
}

// Function to convert Python object to DataKrev
bool convertPythonToDataKrev(PyObject* pyDataKrev, DataKrev& dataKrev) {
    if (!PyTuple_Check(pyDataKrev) || PyTuple_Size(pyDataKrev) != 2) {
        PyErr_SetString(PyExc_TypeError, "Invalid DataKrev format");
        return false;
    }

    PyObject* pyNodeList = PyTuple_GetItem(pyDataKrev, 0);
    PyObject* pyLevelObj = PyTuple_GetItem(pyDataKrev, 1);

    if (!PyList_Check(pyNodeList) || !PyLong_Check(pyLevelObj)) {
        PyErr_SetString(PyExc_TypeError, "Invalid DataKrev format");
        return false;
    }

    dataKrev.level = PyLong_AsLong(pyLevelObj);

    size_t nodeListSize = PyList_Size(pyNodeList);
    dataKrev.node_list.clear();
    for (size_t i = 0; i < nodeListSize; ++i) {
        GGMNode node(0, 0);
        PyObject* pyNode = PyList_GetItem(pyNodeList, i);
        if (!convertPythonToGGMNode(pyNode, node)) {
            PyErr_SetString(PyExc_TypeError, "Invalid GGMNode format");
            return false;
        }
        dataKrev.node_list.push_back(node);
    }

    return true;
}

std::vector<DataPair> convertPythonToDataPairVector(PyObject* pyDataPairList) {
    std::vector<DataPair> dataPairs;

    // Check if the input is a list
    if (!PyList_Check(pyDataPairList)) {
        PyErr_SetString(PyExc_TypeError, "Expected a list of DataPair objects.");
        return dataPairs;
    }

    Py_ssize_t numPairs = PyList_Size(pyDataPairList);
    for (Py_ssize_t i = 0; i < numPairs; ++i) {
        PyObject* pyDataPair = PyList_GetItem(pyDataPairList, i);

        // Check if the element is a tuple
        if (!PyTuple_Check(pyDataPair) || PyTuple_Size(pyDataPair) != 2) {
            PyErr_SetString(PyExc_TypeError, "Each DataPair should be a tuple (tagString, ciphertext_list).");
            return dataPairs;
        }

        PyObject* pyTagString = PyTuple_GetItem(pyDataPair, 0);
        PyObject* pyCiphertextList = PyTuple_GetItem(pyDataPair, 1);

        // Check if tagString is bytes and ciphertext_list is a list
        if (!PyBytes_Check(pyTagString) || !PyList_Check(pyCiphertextList)) {
            PyErr_SetString(PyExc_TypeError, "tagString should be bytes and ciphertext_list should be a list.");
            return dataPairs;
        }

        DataPair dataPair;

        // Copy tagString data
        Py_ssize_t tagStringSize = PyBytes_Size(pyTagString);
        if (tagStringSize != DIGEST_SIZE) {
            PyErr_SetString(PyExc_ValueError, "tagString size mismatch.");
            return dataPairs;
        }
        memcpy(dataPair.tagString, PyBytes_AsString(pyTagString), tagStringSize);

        // Process ciphertext_list
        Py_ssize_t numCiphertexts = PyList_Size(pyCiphertextList);
        for (Py_ssize_t j = 0; j < numCiphertexts; ++j) {
            PyObject* pyCiphertext = PyList_GetItem(pyCiphertextList, j);
            if (!PyBytes_Check(pyCiphertext)) {
                PyErr_SetString(PyExc_TypeError, "Each element in ciphertext_list should be bytes.");
                return dataPairs;
            }

            Py_ssize_t ciphertextSize = PyBytes_Size(pyCiphertext);
            if (ciphertextSize != AES_BLOCK_SIZE + sizeof(int)) {
                PyErr_SetString(PyExc_ValueError, "Invalid size for ciphertext element.");
                return dataPairs;
            }

            // Extract and process ciphertext data
            const char* ciphertextData = PyBytes_AsString(pyCiphertext);
            std::string ciphertext(ciphertextData, ciphertextSize);
            dataPair.ciphertext_list.push_back(ciphertext);
        }

        // Add the constructed DataPair to the vector
        dataPairs.push_back(dataPair);
    }

    return dataPairs;
}


static PyObject* cSRESetup(PyObject *self , PyObject *args)
{
	PyObject* ret;
	int ggm_size, hashsize;
	int instanceID;


    if(!PyArg_ParseTuple(args , "iii" , &instanceID, &ggm_size, &hashsize))
    {
      return NULL;
    }	

    sre_ins[instanceID] = new SRE_Encap(ggm_size,hashsize);
    uint8_t tag[DIGEST_SIZE]{};
    // sre_ins[instanceID]->revoke(tag);

    ret = (PyObject *)Py_BuildValue("i" , instanceID);
    return ret;	
}

static PyObject* cSREEnc(PyObject *self , PyObject *args)
{

	PyObject *ret;
	int instanceID;
	int ind;
	const char* tagstring;
    if(!PyArg_ParseTuple(args , "iis" , &instanceID, &ind, &tagstring))
    {
      return NULL;
    }

    uint8_t tag[DIGEST_SIZE];
	unsigned char* temptag = reinterpret_cast<unsigned char*>(const_cast<char*>(tagstring));
	sha256_digest(temptag, strlen(tagstring), tag);

    DataPair data = sre_ins[instanceID]->encrypt(ind, tag);

    ret = (PyObject*)convertDataPairToPython(data);

    return ret;	
}

static PyObject* cSRERev(PyObject *self , PyObject *args)
{
	PyObject* ret;
	int instanceID;
	const char* tagstring;

	if(!PyArg_ParseTuple(args, "is", &instanceID, &tagstring))
	{
		return NULL;
	}

    uint8_t tag[DIGEST_SIZE];
	unsigned char* temptag = reinterpret_cast<unsigned char*>(const_cast<char*>(tagstring));
	sha256_digest(temptag, strlen(tagstring), tag);

   	sre_ins[instanceID]->revoke(tag);

	ret = (PyObject *)Py_BuildValue("i" , 1);
    return ret;	
}

static PyObject* cSREsKey(PyObject *self , PyObject *args)
{
	PyObject* ret;
	int instanceID;
	if(!PyArg_ParseTuple(args, "i", &instanceID))
	{
		return NULL;
	}

	DataKrev skey = sre_ins[instanceID]->Krev();

	ret = convertDataKrevToPython(skey);

	return ret;
}

static PyObject* cSREDec(PyObject *self, PyObject *args)
{
	PyObject* ret, *input_datapairs, *input_skey;
	int instanceID;
	if(!PyArg_ParseTuple(args, "iOO", &instanceID, &input_skey, &input_datapairs))
	{
		return NULL;
	}
	vector<DataPair> datas = convertPythonToDataPairVector(input_datapairs);

	DataKrev skey;
	convertPythonToDataKrev(input_skey, skey);

	vector<int> dec_ret = sre_ins[instanceID]->Dec(skey,datas);
	ret = convertVectorIntToPython(dec_ret);

	return ret;
}


static PyObject* cSREDecG(PyObject *self, PyObject *args)
{
	PyObject* ret, *input_datapairs, *input_skey;
	int instanceID;
	if(!PyArg_ParseTuple(args, "iOO", &instanceID, &input_skey, &input_datapairs))
	{
		return NULL;
	}
	vector<DataPair> datas = convertPythonToDataPairVector(input_datapairs);
	DataKrev skey;
	convertPythonToDataKrev(input_skey, skey);

	vector<int> dec_ret = sre_ins[instanceID]->Dec_Greed(skey,datas);
	ret = convertVectorIntToPython(dec_ret);

	return ret;
}




static PyMethodDef
cSRE_methods[] = {
	{"Setup", cSRESetup, METH_VARARGS},
	{"Enc", cSREEnc, METH_VARARGS},
	{"Rev", cSRERev, METH_VARARGS},
	{"sKey", cSREsKey, METH_VARARGS},
	{"Dec", cSREDec, METH_VARARGS},
	{"DecG", cSREDecG, METH_VARARGS},
	{0,0,0},
};


static struct PyModuleDef
cSRE = {
    PyModuleDef_HEAD_INIT,
    "cSRE",
    "",
    -1,
    cSRE_methods,
    NULL,
    NULL,
    NULL,
    NULL
};


PyMODINIT_FUNC PyInit_cSRE(void)
{
    return PyModule_Create(&cSRE);
}