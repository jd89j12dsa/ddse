"""
Copyright (c) 2016, Kevin Lewi
 
Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

"""
Implementation of function-hiding inner product encryption (FHIPE).
"""

import sys, os, math, pdb

# Path hack
sys.path.append(os.path.abspath('charm'))
sys.path.append(os.path.abspath('../charm'))

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import objectToBytes,bytesToObject

from subprocess import call, Popen, PIPE

def setup(n, group_name = 'MNT159', simulated = False):
  """
  Performs the setup algorithm for IPE.
  
  This function samples the generators from the group, specified optionally by 
  "group_name". This variable must be one of a few set of strings specified by 
  Charm.

  Then, it invokes the C program ./gen_matrices, which samples random matrices 
  and outputs them back to this function. The dimension n is supplied, and the 
  prime is chosen as the order of the group. Additionally, /dev/urandom is 
  sampled for a random seed which is passed to ./gen_matrices.

  Finally, the function constructs the matrices that form the secret key and 
  publishes the pulbic marapeters and secret key (pp, sk).
  """

  group = PairingGroup(group_name)
  g1 = group.random(G1)
  g2 = group.random(G2)
  assert g1.initPP(), "ERROR: Failed to init pre-computation table for g1."
  assert g2.initPP(), "ERROR: Failed to init pre-computation table for g2."
  
  proc = Popen(
    [
      os.path.dirname(os.path.realpath(__file__)) + '/gen_matrices',
      str(n),
      str(group.order()),
      "1" if simulated else "0",
      ""
    ],
    stdout=PIPE
  )
  detB_str = proc.stdout.readline().decode()
  B_str = proc.stdout.readline().decode()
  Bstar_str = proc.stdout.readline().decode()

  detB = int(detB_str)
  B = parse_matrix(B_str, group)
  Bstar = parse_matrix(Bstar_str, group)

  pp = (group,)
  sk = (detB, B, Bstar, group, g1, g2)
  return (pp, sk)

def keygen(sk, x): # x is a list for vector
  """
  Performs the keygen algorithm for IPE.
  """

  (detB, B, Bstar, group, g1, g2) = sk
  n = len(x)
  alpha = group.hash(args="1",type=ZR)

  k1 = [0] * n
  for j in range(n):
    sum = 0
    for i in range(n):
      sum += x[i] * B[i][j]
    k1[j] = alpha * sum

  for i in range(n):
    k1[i] = g1 ** k1[i]
  
  return objectToBytes(k1 , group)
  
def encrypt(sk, x):
  """
  Performs the encrypt algorithm for IPE.
  """

  (detB, B, Bstar, group, g1, g2) = sk
  n = len(x)
  beta = group.hash(args="1",type=ZR)

  c1 = [0] * n
  for j in range(n):
    sum = 0
    for i in range(n):
      sum += x[i] * Bstar[i][j]
    c1[j] = beta * sum
  
  for i in range(n):
    c1[i] = g2 ** c1[i]

  #pdb.set_trace()

  return objectToBytes(c1 , group)

def decrypt(pp, skx, cty, max_innerprod = 100):
  """
  Performs the decrypt algorithm for IPE on a secret key skx and ciphertext cty. 
  The output is the inner product <x,y>, so long as it is in the range 
  [0,max_innerprod].
  """
  (group,) = pp
  k1 = bytesToObject(skx, group)
  c1 = bytesToObject(cty, group)

  t1 = innerprod_pair(c1, k1)
  #t2 = pair(c2, k2)
  
  return objectToBytes(t1, group)

def parse_matrix(matrix_str, group):
  """
  Parses the matrix as output from the call to ./gen_matrices.

  The first number is the number of rows, and the second number is the number 
  of columns. Then, the entries of the matrix follow. These are stored and 
  returned as a matrix.

  This function also needs the pairing group description to be passed in as a 
  parameter.
  """
  L = matrix_str.split(" ")
  rows, cols = int(L[0]), int(L[1])
  A = [[0]*cols for _ in range(rows)]
  L = L[3:]
  assert rows == cols
  assert len(L) == rows * cols
  for i in range(len(L)):
    A[int(i / rows)][i % rows] = group.init(ZR, int(L[i]))
  return A

def innerprod_pair(x, y):
  """
  Computes the inner product of two vectors x and y "in the exponent", using 
  pairings.
  """

  assert len(x) == len(y)
  L = map(lambda i: pair(x[i], y[i]), range(len(x)))
  ret = 1
  for i in L:
    ret *= i
  return ret

def solve_dlog_naive(g, h, dlog_max):
  """
  Naively attempts to solve for the discrete log x, where g^x = h, via trial and 
  error. Assumes that x is at most dlog_max.
  """

  for j in range(dlog_max):
    if g ** j == h:
      return j
  return -1

def solve_dlog_bsgs(g, h, dlog_max):
  """
  Attempts to solve for the discrete log x, where g^x = h, using the Baby-Step 
  Giant-Step algorithm. Assumes that x is at most dlog_max.
  """

  alpha = int(math.ceil(math.sqrt(dlog_max))) + 1
  g_inv = g ** -1
  tb = {}
  for i in range(alpha + 1):
    tb[(g ** (i * alpha)).__str__()] = i
    for j in range(alpha + 1):
      s = (h * (g_inv ** j)).__str__()
      if s in tb:
        i = tb[s]
        return i * alpha + j
  return -1

