################################################################################
# Example usage



import os
import shutil

if os.path.exists("logs/decrypt.log"):
    os.remove("logs/decrypt.log")


import logging
logging.basicConfig(
    filename="logs/decrypt.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'testing')))
import time
from services.lok_service import LokService
from JS2PY import LOK_JS2PY

lok = LOK_JS2PY("testing/js_testing/test6.wasm")

import numpy as np
with open('70645.bin', 'rb') as ifile:
    heap8 = np.frombuffer(ifile.read(), dtype=np.uint8)

lok.reallocBuffer(heap8.size)
np.copyto(lok.HEAP8, heap8)

#decryption
# input: a, b, c
# input is gzip >> base64.decode
# starting index of input -16

# c is always 0

# return : the index of the output -16
{0: 279504540, 1: 48, 2: 261487248, 3: 35, 4: 0}
#279504540 in index
# 261487248 out index
# 48 size of regionhash
# 35 size of output? always 35?

output_idx = lok.decryption(279504540,48, 261487248, 35, 0)


with open('after3.bin', 'wb') as ifile:
    ifile.write(bytes(lok.HEAP8))
print('done', output_idx)
