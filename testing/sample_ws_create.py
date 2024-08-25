################################################################################
# Example usage



import os
try:
    os.remove("logs/wasm.log")
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

lok = LOK_JS2PY("testing/js_testing/test4.wasm")
lok.customstore(5948976, 11191872)
lok.customstore(5948960, 5524807)
lok._AT_INIT()
a = LokService()
a.login()
token = a.accessToken
# lok.customstore(5271516, 26750912) # this is setup somewhere, manual modify
# lok.customstore(5917317, 257) # this is setup somewhere, manual modify
# lok.customstore(5913976, 3211313340) # this is setup somewhere, manual modify
# lok.customstore(5913984, 176) # this is setup somewhere, manual modify
# lok.customstore(5913996, 643977312)

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