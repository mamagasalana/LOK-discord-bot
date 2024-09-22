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

lok = LOK_JS2PY("testing/js_testing/test5.wasm")
lok.HEAP32[5948976//4] = 11191872
lok.HEAP32[5948960//4] =  5524807


# 2024-09-21 22:27:15,538 - INFO - '_JS_FileSystem_Sync' () ||| {5914040: 30562776, 5949364: 1, 5914048: 30475680, 5913976: 156, 5913992: 11191872, 5913996: 0, 5914000: 30600048}
# 2024-09-21 22:27:15,539 - ERROR - _JS_FileSystem_Sync not implemented

# 2024-09-21 22:27:15,979 - INFO - '_JS_FileSystem_Sync' () ||| {5914040: 30835144, 5949364: 0, 5914048: 30475680, 5913976: 262412, 5913992: 11191872, 5913996: 30961520, 5914000: 30964016}
# 2024-09-21 22:27:15,979 - ERROR - _JS_FileSystem_Sync not implemented

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