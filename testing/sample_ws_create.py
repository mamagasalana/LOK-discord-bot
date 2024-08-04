################################################################################
# Example usage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'testing')))
import time
from services.lok_service import LokService
from JS2PY import LOK_JS2PY

try:
    os.remove("logs/wasm.log")
except:
    pass

lok = LOK_JS2PY("testing/js_testing/test2.wasm")
a = LokService()
a.login()
token = a.accessToken

URL = f"wss://socf-lok-live.leagueofkingdoms.com/socket.io/?EIO=4&transport=websocket&token={token}"
lok._WS_Create(URL, '', 17058,17691,14198,17692,14199 )
print('\ndebug started')
# set breakpoint at 
#  def _WS_Create
# >> on_message_wrapper


# 2024-07-28 21:15:01,881 - INFO - _syscall4 not implemented
# Fill missing function if any

time.sleep(300)