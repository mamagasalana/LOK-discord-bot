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

lok = LOK_JS2PY("testing/js_testing/test.wasm")
lok.HEAP32[5948976>>2] = 11191872
lok.HEAP32[5948960>>2] =  5524807

lok.HEAP32[5950900>>2] =124
# processWasmFrameworkJob
#5914000 :30988952
# enlargeMemory
# 2024-09-22 23:58:11,203 - INFO - '_glGetString' (index == 7937) ||| {5914040: 30835144, 5949364: 0, 5914048: 30475680, 5913976: 12, 5913992: 11191872, 5913996: 30965512, 5914000: 30985856}
# 2024-09-22 23:58:11,204 - INFO - '_glGetIntegerv' (index == 33309) && (a1 == 5949544) ||| {5914040: 30835144, 5949364: 0, 5914048: 30475680, 5913976: 4, 5913992: 11191872, 5913996: 30965512, 5914000: 30985856}
# 2024-09-22 23:58:17,568 - INFO - '_glGetStringi' (index == 7939) && (a1 == 0) ||| {5914040: 30835144, 5949364: 0, 5914048: 30475680, 5913976: 4, 5913992: 11191872, 5913996: 30965512, 5914000: 30985856}
# 2024-09-22 23:59:13,036 - INFO - 'getTotalMemory' () ||| {5914040: 30835144, 5949364: 0, 5914048: 30475680, 5913976: 4, 5913992: 11191872, 5913996: 30965560, 5914000: 30986184}

#2024-09-24 21:03:03,369 - INFO - from funcname 8635, {0: 30966400, 1: 30997968, 5913976: 4, 5913992: 11191872, 5913996: 0, 5914000: 31002192, 5914040: 30965560, 5914048: 30475680, 5949364: 0}
# _glGenTextures

#2024-09-28 02:12:54,259 - INFO - '_syscall140' (index == 140) && (a1 == 5949872) ||| return 0 ||| {5949536: 0, 12768780: 32, 30976960: 17854, 5914040: 35240488, 5949364: 0, 5914048: 35261432, 5913976: 134414384, 5913992: 11191872, 5913996: 33723304, 5914000: 35481384

#30976960: 17967, 5914040 :28776240
#30976960: 17854,   : 28778104,
# 2024-09-28 23:38:38,641 - INFO - 'enlargeMemory' () ||| return True ||| {5949536: 14156048, 12768780: 32, 30976960: 17854, 5914040: 28778104, 5949364: 0, 5914048: 29240520, 5913976: 0, 5913992: 11191872, 5913996: 0, 5914000: 33554352}

lok._AT_INIT()
lok._AT_MAIN()
a = LokService()
a.login()
token = a.accessToken

URL = f"wss://socf-lok-live.leagueofkingdoms.com/socket.io/?EIO=4&transport=websocket&token={token}"
lok._WS_Create(URL, '', 17058,17691,14198,17692,14199 )
print('\ndebug started')
# set breakpoint at 
#  def _WS_Create
# >> on_message_wrapper

#track this const 5913980
#track this const 5913984
#track this const 5913988
# culprit found 5914000


# 2024-08-25 00:30:48,424 - INFO - from funcname 93115, placeholder 3 : 4096
# 2024-08-25 00:30:48,425 - INFO - from funcname 93115, placeholder 4 : 1114112
# expect 11191872 for from funcname 93115, placeholder 3
# expect 0 for from funcname 93115, placeholder 4

# 2024-07-28 21:15:01,881 - INFO - _syscall4 not implemented
# Fill missing function if any
time.sleep(300)