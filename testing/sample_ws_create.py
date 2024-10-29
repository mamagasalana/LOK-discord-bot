################################################################################
# Example usage



import os
import shutil

if os.path.exists("logs/wasm.log"):
    os.remove("logs/wasm.log")

try:
    directory = 'testing/js_testing/JS_MOUNT/'
    source_directory = 'testing/js_testing/JS_MOUNT2/'
    # Loop through and remove each file and directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
    
    shutil.copytree(source_directory, directory, dirs_exist_ok=True)

except Exception as e:
    print(e)

import logging
# from FS import FS
logging.basicConfig(
    filename="logs/wasm.log",
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

# lok.HEAP32[5948976>>2] = 11191872
# lok.HEAP32[5948960>>2] =  5524807
# lok._AT_INIT()
# lok._AT_MAIN()

import numpy as np
with open('before2.bin', 'rb') as ifile:
    heap8 = np.frombuffer(ifile.read(), dtype=np.uint8)

lok.reallocBuffer(heap8.size)
np.copyto(lok.HEAP8, heap8)

lok.START_DEBUG = True
lok.dynCall_vi(17961, 0)

with open('after.bin', 'wb') as ifile:
    ifile.write(bytes(lok.HEAP8))
print('done')

# session = lok.session
# headers= {
#     'content-type' : 'application/x-www-form-urlencoded',
#     'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
#     'x-access-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NjdhYjVlNTNiYTdjNzYyZDEyYTk4YWEiLCJraW5nZG9tSWQiOiI2NjdhYjVmOGYyNjk3Y2E4ODkyYTY3ODEiLCJ3b3JsZElkIjoyNiwidmVyc2lvbiI6MTc3NSwiYXV0aFR5cGUiOiJlbWFpbCIsInBsYXRmb3JtIjoid2ViIiwidGltZSI6MTcyOTkxOTY0NDE3MCwiY2xpZW50WG9yIjoiMCIsImlwIjoiMTc1LjE0My4yMzUuMjQwIiwiaWF0IjoxNzI5OTE5NjQ0LCJleHAiOjE3MzA1MjQ0NDQsImlzcyI6Im5vZGdhbWVzLmNvbSIsInN1YiI6InVzZXJJbmZvIn0.4MbDpQHDGXC3wss328ZOcTHbwUHXOogESvGlQ7rgo20'
# }
# data = {'json': 'VRg='}
# r = session.post("https://api-lok-live.leagueofkingdoms.com/api/kingdom/task/all", headers=headers, data=data)
# lok.rpcs[387] = r
# response = r.result().content
# byteArray = np.frombuffer(response, dtype=np.uint8)
# buffer = lok._malloc(len(byteArray))
# lok.HEAPU8[buffer: buffer+len(byteArray)] = byteArray
# lok.dynCall_viiiii(1894, 387, 200, buffer, len(byteArray), 0)
# with open('after.bin', 'wb') as ifile:
#     ifile.write(bytes(lok.HEAP8))
# print('done')

# a = LokService()
# a.login()
# token = a.accessToken

# logging.info("Started")
# lok.START_DEBUG = True
# URL = f"wss://socf-lok-live.leagueofkingdoms.com/socket.io/?EIO=4&transport=websocket&token={token}"
# lok._WS_Create(URL, '', 17058,17691,14198,17692,14199)
# print('\ndebug started')

