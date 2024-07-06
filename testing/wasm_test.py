from wasmtime import Config, Store, Engine, Module, FuncType, Func, ValType, Instance, Limits, MemoryType, Global, GlobalType, Val, Memory, Table, TableType

config = Config()
config.wasm_multi_value = True
engine = Engine()

# Load the Wasm module
wasm_module = Module.from_file(engine, "testing/LOK.wasm")
store = Store(engine)
# Create memory
limits = Limits(512, None)  # Replace None with maximum size if needed
memory_type = MemoryType(limits)
memory = Memory(store, memory_type)

# Create table
limits = Limits(181773, 181773)
table_type = TableType(ValType.funcref(), limits)
table = Table(store, table_type, None)

mutable = False  # Mutable
global_type32 = GlobalType(ValType.i32(), mutable)
global_type64 = GlobalType(ValType.f64(), mutable)
# Create globals
global_tableBase = Global(store, global_type32, Val.i32(0))
global_DYNAMICTOP_PTR = Global(store, global_type32, Val.i32(0))
global_STACKTOP = Global(store, global_type32, Val.i32(0))
global_STACK_MAX = Global(store, global_type32, Val.i32(0))

################################################################################
# byte array function
################################################################################
import numpy as np
buffer = np.zeros(536870912, dtype=np.uint8)

# Create views of the buffer with different data types
HEAP8 = buffer.view(np.int8)
HEAP16 = buffer.view(np.int16)
HEAP32 = buffer.view(np.int32)
HEAPU8 = buffer.view(np.uint8)
HEAPU16 = buffer.view(np.uint16)
HEAPU32 = buffer.view(np.uint32)
HEAPF32 = buffer.view(np.float32)
HEAPF64 = buffer.view(np.float64)

def lengthBytesUTF8(s):
    return len(s.encode('utf-8')) 

def stringToUTF8Array(s, outU8Array, outIdx, maxBytesToWrite):
    if not (maxBytesToWrite > 0):
        return 0

    utf8_bytes = s.encode('utf-8')
    bytes_to_copy = min(len(utf8_bytes), maxBytesToWrite - 1)  # Leave space for the null terminator

    # Copy the bytes to the output array
    outU8Array[outIdx:outIdx + bytes_to_copy] = np.frombuffer(utf8_bytes[:bytes_to_copy], dtype=np.uint8)
    outU8Array[outIdx + bytes_to_copy] = 0  # Null terminator

    return bytes_to_copy

def UTF8ToString(ptr):
    return UTF8ArrayToString(HEAPU8, ptr)

def UTF8ArrayToString():
    pass

def Pointer_stringify(ptr, length=None):
    if (length == 0 or  not ptr):
        return ""
    hasUtf = 0
    i = 0
    while True:
        t = HEAPU8[ptr + i]
        hasUtf |= t
        if t == 0 and not length:
            break
        i += 1
        if length and i == length:
            break

    if not length:
        length = i

    ret = ""
    if hasUtf < 128:
        MAX_CHUNK = 1024
        while (length > 0):
            curr = "".join(chr(HEAPU8[ptr + j]) for j in range(min(length, MAX_CHUNK)))
            ret += curr
            ptr += MAX_CHUNK
            length -= MAX_CHUNK
        return ret
    
    return UTF8ToString(ptr)
################################################################################
# Example usage
s = "Hello, 世界"
out_idx = 0
max_bytes_to_write = 100

num_bytes = stringToUTF8Array(s, HEAPU8, out_idx, max_bytes_to_write)
print(num_bytes)  # Output should be the length in bytes
print(HEAPU8[:num_bytes + 1])  # Output should contain the UTF-8 encoded string and null terminator
ptr = 1  # Assuming the string starts at index 0
out = Pointer_stringify(ptr, 2)  # Output shoul

################################################################################
# The following section contains wasm function
################################################################################
def abort(param0):
    print("abort not implemented")
    return 

def enlargeMemory():
    print("enlargeMemory not implemented")
    return 0

def getTotalMemory():
    print("getTotalMemory not implemented")
    return 0

def abortOnCannotGrowMemory():
    print("abortOnCannotGrowMemory not implemented")
    return 0

def invoke_dddi(param0,param1,param2,param3):
    print("invoke_dddi not implemented")
    return 0

def invoke_dii(param0,param1,param2):
    print("invoke_dii not implemented")
    return 0

def invoke_diii(param0,param1,param2,param3):
    print("invoke_diii not implemented")
    return 0

def invoke_diiid(param0,param1,param2,param3,param4):
    print("invoke_diiid not implemented")
    return 0

def invoke_diiii(param0,param1,param2,param3,param4):
    print("invoke_diiii not implemented")
    return 0

def invoke_ffffi(param0,param1,param2,param3,param4):
    print("invoke_ffffi not implemented")
    return 0

def invoke_fffi(param0,param1,param2,param3):
    print("invoke_fffi not implemented")
    return 0

def invoke_fi(param0,param1):
    print("invoke_fi not implemented")
    return 0

def invoke_fii(param0,param1,param2):
    print("invoke_fii not implemented")
    return 0

def invoke_fiifi(param0,param1,param2,param3,param4):
    print("invoke_fiifi not implemented")
    return 0

def invoke_fiifii(param0,param1,param2,param3,param4,param5):
    print("invoke_fiifii not implemented")
    return 0

def invoke_fiii(param0,param1,param2,param3):
    print("invoke_fiii not implemented")
    return 0

def invoke_fiiif(param0,param1,param2,param3,param4):
    print("invoke_fiiif not implemented")
    return 0

def invoke_fiiii(param0,param1,param2,param3,param4):
    print("invoke_fiiii not implemented")
    return 0

def invoke_i(param0):
    print("invoke_i not implemented")
    return 0

def invoke_ifi(param0,param1,param2):
    print("invoke_ifi not implemented")
    return 0

def invoke_ii(param0,param1):
    print("invoke_ii not implemented")
    return 0

def invoke_iifii(param0,param1,param2,param3,param4):
    print("invoke_iifii not implemented")
    return 0

def invoke_iii(param0,param1,param2):
    print("invoke_iii not implemented")
    return 0

def invoke_iiifi(param0,param1,param2,param3,param4):
    print("invoke_iiifi not implemented")
    return 0

def invoke_iiii(param0,param1,param2,param3):
    print("invoke_iiii not implemented")
    return 0

def invoke_iiiifii(param0,param1,param2,param3,param4,param5,param6):
    print("invoke_iiiifii not implemented")
    return 0

def invoke_iiiii(param0,param1,param2,param3,param4):
    print("invoke_iiiii not implemented")
    return 0

def invoke_iiiiii(param0,param1,param2,param3,param4,param5):
    print("invoke_iiiiii not implemented")
    return 0

def invoke_iiiiiii(param0,param1,param2,param3,param4,param5,param6):
    print("invoke_iiiiiii not implemented")
    return 0

def invoke_iiiiiiii(param0,param1,param2,param3,param4,param5,param6,param7):
    print("invoke_iiiiiiii not implemented")
    return 0

def invoke_iiiiiiiii(param0,param1,param2,param3,param4,param5,param6,param7,param8):
    print("invoke_iiiiiiiii not implemented")
    return 0

def invoke_iiiiiiiiii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
    print("invoke_iiiiiiiiii not implemented")
    return 0

def invoke_iiiiiiiiiii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
    print("invoke_iiiiiiiiiii not implemented")
    return 0

def invoke_v(param0):
    print("invoke_v not implemented")
    return 

def invoke_vi(param0,param1):
    print("invoke_vi not implemented")
    return 

def invoke_vidiii(param0,param1,param2,param3,param4,param5):
    print("invoke_vidiii not implemented")
    return 

def invoke_vifffi(param0,param1,param2,param3,param4,param5):
    print("invoke_vifffi not implemented")
    return 

def invoke_vifi(param0,param1,param2,param3):
    print("invoke_vifi not implemented")
    return 

def invoke_vifii(param0,param1,param2,param3,param4):
    print("invoke_vifii not implemented")
    return 

def invoke_vii(param0,param1,param2):
    print("invoke_vii not implemented")
    return 

def invoke_viidi(param0,param1,param2,param3,param4):
    print("invoke_viidi not implemented")
    return 

def invoke_viidii(param0,param1,param2,param3,param4,param5):
    print("invoke_viidii not implemented")
    return 

def invoke_viiff(param0,param1,param2,param3,param4):
    print("invoke_viiff not implemented")
    return 

def invoke_viiffi(param0,param1,param2,param3,param4,param5):
    print("invoke_viiffi not implemented")
    return 

def invoke_viifi(param0,param1,param2,param3,param4):
    print("invoke_viifi not implemented")
    return 

def invoke_viifii(param0,param1,param2,param3,param4,param5):
    print("invoke_viifii not implemented")
    return 

def invoke_viii(param0,param1,param2,param3):
    print("invoke_viii not implemented")
    return 

def invoke_viiif(param0,param1,param2,param3,param4):
    print("invoke_viiif not implemented")
    return 

def invoke_viiii(param0,param1,param2,param3,param4):
    print("invoke_viiii not implemented")
    return 

def invoke_viiiii(param0,param1,param2,param3,param4,param5):
    print("invoke_viiiii not implemented")
    return 

def invoke_viiiiii(param0,param1,param2,param3,param4,param5,param6):
    print("invoke_viiiiii not implemented")
    return 

def invoke_viiiiiii(param0,param1,param2,param3,param4,param5,param6,param7):
    print("invoke_viiiiiii not implemented")
    return 

def invoke_viiiiiiifddfii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,param11,param12,param13):
    print("invoke_viiiiiiifddfii not implemented")
    return 

def invoke_viiiiiiiffffii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,param11,param12,param13):
    print("invoke_viiiiiiiffffii not implemented")
    return 

def invoke_viiiiiiifiifii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,param11,param12,param13):
    print("invoke_viiiiiiifiifii not implemented")
    return 

def invoke_viiiiiiii(param0,param1,param2,param3,param4,param5,param6,param7,param8):
    print("invoke_viiiiiiii not implemented")
    return 

def invoke_viiiiiiiii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
    print("invoke_viiiiiiiii not implemented")
    return 

def invoke_viiiiiiiiii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
    print("invoke_viiiiiiiiii not implemented")
    return 

def _ES_AddEventHandler(param0,param1):
    print("_ES_AddEventHandler not implemented")
    return 

def _ES_Close(param0):
    print("_ES_Close not implemented")
    return 

def _ES_Create(param0,param1,param2,param3,param4):
    print("_ES_Create not implemented")
    return 0

def _ES_IsSupported():
    print("_ES_IsSupported not implemented")
    return 0

def _ES_Release(param0):
    print("_ES_Release not implemented")
    return 

def _GetInputFieldSelectionEnd():
    print("_GetInputFieldSelectionEnd not implemented")
    return 0

def _GetInputFieldSelectionStart():
    print("_GetInputFieldSelectionStart not implemented")
    return 0

def _GetInputFieldValue():
    print("_GetInputFieldValue not implemented")
    return 0

def _HideInputField():
    print("_HideInputField not implemented")
    return 

def _IsInputFieldActive():
    print("_IsInputFieldActive not implemented")
    return 0

def _JS_Cursor_SetImage(param0,param1):
    print("_JS_Cursor_SetImage not implemented")
    return 

def _JS_Cursor_SetShow(param0):
    print("_JS_Cursor_SetShow not implemented")
    return 

def _JS_Eval_ClearInterval(param0):
    print("_JS_Eval_ClearInterval not implemented")
    return 

def _JS_Eval_OpenURL(param0):
    print("_JS_Eval_OpenURL not implemented")
    return 

def _JS_Eval_SetInterval(param0,param1,param2):
    print("_JS_Eval_SetInterval not implemented")
    return 0

def _JS_FileSystem_Initialize():
    print("_JS_FileSystem_Initialize not implemented")
    return 

def _JS_FileSystem_Sync():
    print("_JS_FileSystem_Sync not implemented")
    return 

def _JS_Log_Dump(param0,param1):
    print("_JS_Log_Dump not implemented")
    return 

def _JS_Log_StackTrace(param0,param1):
    print("_JS_Log_StackTrace not implemented")
    return 

def _JS_Sound_Create_Channel(param0,param1):
    print("_JS_Sound_Create_Channel not implemented")
    return 0

def _JS_Sound_GetLength(param0):
    print("_JS_Sound_GetLength not implemented")
    return 0

def _JS_Sound_GetLoadState(param0):
    print("_JS_Sound_GetLoadState not implemented")
    return 0

def _JS_Sound_Init():
    print("_JS_Sound_Init not implemented")
    return 

def _JS_Sound_Load(param0,param1):
    print("_JS_Sound_Load not implemented")
    return 0

def _JS_Sound_Load_PCM(param0,param1,param2,param3):
    print("_JS_Sound_Load_PCM not implemented")
    return 0

def _JS_Sound_Play(param0,param1,param2,param3):
    print("_JS_Sound_Play not implemented")
    return 

def _JS_Sound_ReleaseInstance(param0):
    print("_JS_Sound_ReleaseInstance not implemented")
    return 0

def _JS_Sound_ResumeIfNeeded():
    print("_JS_Sound_ResumeIfNeeded not implemented")
    return 

def _JS_Sound_Set3D(param0,param1):
    print("_JS_Sound_Set3D not implemented")
    return 

def _JS_Sound_SetListenerOrientation(param0,param1,param2,param3,param4,param5):
    print("_JS_Sound_SetListenerOrientation not implemented")
    return 

def _JS_Sound_SetListenerPosition(param0,param1,param2):
    print("_JS_Sound_SetListenerPosition not implemented")
    return 

def _JS_Sound_SetLoop(param0,param1):
    print("_JS_Sound_SetLoop not implemented")
    return 

def _JS_Sound_SetLoopPoints(param0,param1,param2):
    print("_JS_Sound_SetLoopPoints not implemented")
    return 

def _JS_Sound_SetPaused(param0,param1):
    print("_JS_Sound_SetPaused not implemented")
    return 

def _JS_Sound_SetPitch(param0,param1):
    print("_JS_Sound_SetPitch not implemented")
    return 

def _JS_Sound_SetPosition(param0,param1,param2,param3):
    print("_JS_Sound_SetPosition not implemented")
    return 

def _JS_Sound_SetVolume(param0,param1):
    print("_JS_Sound_SetVolume not implemented")
    return 

def _JS_Sound_Stop(param0,param1):
    print("_JS_Sound_Stop not implemented")
    return 

def _JS_SystemInfo_GetBrowserName(param0,param1):
    print("_JS_SystemInfo_GetBrowserName not implemented")
    return 0

def _JS_SystemInfo_GetBrowserVersionString(param0,param1):
    print("_JS_SystemInfo_GetBrowserVersionString not implemented")
    return 0

def _JS_SystemInfo_GetCanvasClientSize(param0,param1,param2):
    print("_JS_SystemInfo_GetCanvasClientSize not implemented")
    return 

def _JS_SystemInfo_GetDocumentURL(param0,param1):
    print("_JS_SystemInfo_GetDocumentURL not implemented")
    return 0

def _JS_SystemInfo_GetGPUInfo(param0,param1):
    print("_JS_SystemInfo_GetGPUInfo not implemented")
    return 0

def _JS_SystemInfo_GetLanguage(param0,param1):
    print("_JS_SystemInfo_GetLanguage not implemented")
    return 0

def _JS_SystemInfo_GetMemory():
    print("_JS_SystemInfo_GetMemory not implemented")
    return 0

def _JS_SystemInfo_GetOS(param0,param1):
    print("_JS_SystemInfo_GetOS not implemented")
    return 0

def _JS_SystemInfo_GetPreferredDevicePixelRatio():
    print("_JS_SystemInfo_GetPreferredDevicePixelRatio not implemented")
    return 0

def _JS_SystemInfo_GetScreenSize(param0,param1):
    print("_JS_SystemInfo_GetScreenSize not implemented")
    return 

def _JS_SystemInfo_GetStreamingAssetsURL(param0,param1):
    print("_JS_SystemInfo_GetStreamingAssetsURL not implemented")
    return 0

def _JS_SystemInfo_HasCursorLock():
    print("_JS_SystemInfo_HasCursorLock not implemented")
    return 0

def _JS_SystemInfo_HasFullscreen():
    print("_JS_SystemInfo_HasFullscreen not implemented")
    return 0

def _JS_SystemInfo_HasWebGL():
    print("_JS_SystemInfo_HasWebGL not implemented")
    return 0

def _JS_SystemInfo_IsMobile():
    print("_JS_SystemInfo_IsMobile not implemented")
    return 0

def _JS_Video_CanPlayFormat(param0):
    print("_JS_Video_CanPlayFormat not implemented")
    return 0

def _JS_Video_Create(param0):
    print("_JS_Video_Create not implemented")
    return 0

def _JS_Video_Destroy(param0):
    print("_JS_Video_Destroy not implemented")
    return 

def _JS_Video_Duration(param0):
    print("_JS_Video_Duration not implemented")
    return 0

def _JS_Video_EnableAudioTrack(param0,param1,param2):
    print("_JS_Video_EnableAudioTrack not implemented")
    return 

def _JS_Video_GetAudioLanguageCode(param0,param1):
    print("_JS_Video_GetAudioLanguageCode not implemented")
    return 0

def _JS_Video_GetNumAudioTracks(param0):
    print("_JS_Video_GetNumAudioTracks not implemented")
    return 0

def _JS_Video_Height(param0):
    print("_JS_Video_Height not implemented")
    return 0

def _JS_Video_IsPlaying(param0):
    print("_JS_Video_IsPlaying not implemented")
    return 0

def _JS_Video_IsReady(param0):
    print("_JS_Video_IsReady not implemented")
    return 0

def _JS_Video_Pause(param0):
    print("_JS_Video_Pause not implemented")
    return 

def _JS_Video_Play(param0,param1):
    print("_JS_Video_Play not implemented")
    return 

def _JS_Video_Seek(param0,param1):
    print("_JS_Video_Seek not implemented")
    return 

def _JS_Video_SetEndedHandler(param0,param1,param2):
    print("_JS_Video_SetEndedHandler not implemented")
    return 

def _JS_Video_SetErrorHandler(param0,param1,param2):
    print("_JS_Video_SetErrorHandler not implemented")
    return 

def _JS_Video_SetLoop(param0,param1):
    print("_JS_Video_SetLoop not implemented")
    return 

def _JS_Video_SetMute(param0,param1):
    print("_JS_Video_SetMute not implemented")
    return 

def _JS_Video_SetPlaybackRate(param0,param1):
    print("_JS_Video_SetPlaybackRate not implemented")
    return 

def _JS_Video_SetReadyHandler(param0,param1,param2):
    print("_JS_Video_SetReadyHandler not implemented")
    return 

def _JS_Video_SetSeekedOnceHandler(param0,param1,param2):
    print("_JS_Video_SetSeekedOnceHandler not implemented")
    return 

def _JS_Video_SetVolume(param0,param1):
    print("_JS_Video_SetVolume not implemented")
    return 

def _JS_Video_Time(param0):
    print("_JS_Video_Time not implemented")
    return 0

def _JS_Video_UpdateToTexture(param0,param1):
    print("_JS_Video_UpdateToTexture not implemented")
    return 0

def _JS_Video_Width(param0):
    print("_JS_Video_Width not implemented")
    return 0

def _JS_WebCamVideo_CanPlay(param0):
    print("_JS_WebCamVideo_CanPlay not implemented")
    return 0

def _JS_WebCamVideo_GetDeviceName(param0,param1,param2):
    print("_JS_WebCamVideo_GetDeviceName not implemented")
    return 0

def _JS_WebCamVideo_GetNativeHeight(param0):
    print("_JS_WebCamVideo_GetNativeHeight not implemented")
    return 0

def _JS_WebCamVideo_GetNativeWidth(param0):
    print("_JS_WebCamVideo_GetNativeWidth not implemented")
    return 0

def _JS_WebCamVideo_GetNumDevices():
    print("_JS_WebCamVideo_GetNumDevices not implemented")
    return 0

def _JS_WebCamVideo_GrabFrame(param0,param1,param2,param3):
    print("_JS_WebCamVideo_GrabFrame not implemented")
    return 

def _JS_WebCamVideo_Start(param0):
    print("_JS_WebCamVideo_Start not implemented")
    return 

def _JS_WebCamVideo_Stop(param0):
    print("_JS_WebCamVideo_Stop not implemented")
    return 

def _JS_WebCam_IsSupported():
    print("_JS_WebCam_IsSupported not implemented")
    return 0

def _JS_WebRequest_Abort(param0):
    print("_JS_WebRequest_Abort not implemented")
    return 

def _JS_WebRequest_Create(param0,param1):
    print("_JS_WebRequest_Create not implemented")
    return 0

def _JS_WebRequest_GetResponseHeaders(param0,param1,param2):
    print("_JS_WebRequest_GetResponseHeaders not implemented")
    return 0

def _JS_WebRequest_Release(param0):
    print("_JS_WebRequest_Release not implemented")
    return 

def _JS_WebRequest_Send(param0,param1,param2):
    print("_JS_WebRequest_Send not implemented")
    return 

def _JS_WebRequest_SetProgressHandler(param0,param1,param2):
    print("_JS_WebRequest_SetProgressHandler not implemented")
    return 

def _JS_WebRequest_SetRequestHeader(param0,param1,param2):
    print("_JS_WebRequest_SetRequestHeader not implemented")
    return 

def _JS_WebRequest_SetResponseHandler(param0,param1,param2):
    print("_JS_WebRequest_SetResponseHandler not implemented")
    return 

def _JS_WebRequest_SetTimeout(param0,param1):
    print("_JS_WebRequest_SetTimeout not implemented")
    return 

def _NativeCall(param0,param1):
    print("_NativeCall not implemented")
    return 

def _SetInputFieldSelection(param0,param1):
    print("_SetInputFieldSelection not implemented")
    return 

def _ShowInputField(param0):
    print("_ShowInputField not implemented")
    return 

def _WS_Close(param0,param1,param2):
    print("_WS_Close not implemented")
    return 

class WebSocketClientManager:
    def __init__(self):
        self.webSocketInstances = {}

    @property
    def nextInstanceId(self):
        return len(self.webSocketInstances) +1
    
    def set(self, socket):
        self.webSocketInstances[self.nextInstanceId] =socket
        return self.nextInstanceId

    def get(self, id):
        return self.webSocketInstances[id]

    def _callOnOpen(self, onOpen, id):
        print('debug')
        dynCall_vi(onOpen, id);

    def _callOnBinary(self, onBinary, id, data):
        byteArray = bytearray(data)
        buffer = _malloc(len(byteArray))
        HEAPU8.set(byteArray, buffer)
        dynCall_viii(onBinary, id, buffer, len(byteArray))

    def _callOnText(self, onText, id, data):
        length = lengthBytesUTF8(data) + 1
        buffer = _malloc(length)
        stringToUTF8Array(data, HEAPU8, buffer, length)
        dynCall_vii(onText, id, buffer)

    def _callOnClose(self, onClose, id, code, reason):
        length = lengthBytesUTF8(reason) + 1
        buffer = _malloc(length)
        stringToUTF8Array(reason, HEAPU8, buffer, length)
        dynCall_viii(onClose, id, code, buffer)

    def  _callOnError(errCallback, id, reason):
        length = lengthBytesUTF8(reason) + 1
        buffer = _malloc(length)
        stringToUTF8Array(reason, HEAPU8, buffer, length)
        dynCall_vii(errCallback, id, buffer)

ws =WebSocketClientManager()
import websocket
import threading

def _WS_Create(url, protocol, on_open, on_text, on_binary, on_error, on_close):
    # urlStr = Pointer_stringify(url).replace('+', '%2B').replace('%252F', '%2F')
    # proto = Pointer_stringify(protocol)
    urlStr=  url
    proto = ''
    socket = {
        'onError': on_error,
        'onClose' : on_close,
    }
    socket_impl = websocket.WebSocketApp(urlStr, subprotocols=[proto] if proto else None)
    socket_impl.binaryType = "arraybuffer";
    _id = ws.nextInstanceId

    def on_open_wrapper(ws1):
        ws._callOnOpen(on_open, _id)

    def on_message_wrapper(ws1, message):
        if isinstance(message, (bytes, bytearray)):
            ws._callOnBinary(on_binary, _id, message.data)
        else:
            ws._callOnText(on_text, _id, message.data)

    def on_error_wrapper(ws1, error):
        print(f"{_id} WS_Create - onError")

    def on_close_wrapper(ws1, close_status_code, close_msg):
        print(f"{_id} WS_Create - onClose {close_status_code} {close_msg}")
        ws._callOnClose(on_close, _id, close_status_code, close_msg)

    socket_impl.on_open = on_open_wrapper
    socket_impl.on_message = on_message_wrapper
    socket_impl.on_error = on_error_wrapper
    socket_impl.on_close = on_close_wrapper

    socket['socketImpl'] = socket_impl
    socket_thread = threading.Thread(target=socket_impl.run_forever)
    socket_thread.start()

    return ws.set(socket)

def _WS_GetBufferedAmount(param0):
    print("_WS_GetBufferedAmount not implemented")
    return 0

def _WS_GetState(param0):
    print("_WS_GetState not implemented")
    return 0

def _WS_Release(param0):
    print("_WS_Release not implemented")
    return 

def _WS_Send_Binary(param0,param1,param2,param3):
    print("_WS_Send_Binary not implemented")
    return 0

def _WS_Send_String(param0,param1):
    print("_WS_Send_String not implemented")
    return 0

def _XHR_Abort(param0):
    print("_XHR_Abort not implemented")
    return 

def _XHR_Create(param0,param1,param2,param3,param4):
    print("_XHR_Create not implemented")
    return 0

def _XHR_GetResponseHeaders(param0,param1):
    print("_XHR_GetResponseHeaders not implemented")
    return 

def _XHR_GetStatusLine(param0,param1):
    print("_XHR_GetStatusLine not implemented")
    return 

def _XHR_Release(param0):
    print("_XHR_Release not implemented")
    return 

def _XHR_Send(param0,param1,param2):
    print("_XHR_Send not implemented")
    return 

def _XHR_SetLoglevel(param0):
    print("_XHR_SetLoglevel not implemented")
    return 

def _XHR_SetProgressHandler(param0,param1,param2):
    print("_XHR_SetProgressHandler not implemented")
    return 

def _XHR_SetRequestHeader(param0,param1,param2):
    print("_XHR_SetRequestHeader not implemented")
    return 

def _XHR_SetResponseHandler(param0,param1,param2,param3,param4):
    print("_XHR_SetResponseHandler not implemented")
    return 

def _XHR_SetTimeout(param0,param1):
    print("_XHR_SetTimeout not implemented")
    return 

def ___buildEnvironment(param0):
    print("___buildEnvironment not implemented")
    return 

def ___cxa_allocate_exception(param0):
    print("___cxa_allocate_exception not implemented")
    return 0

def ___cxa_begin_catch(param0):
    print("___cxa_begin_catch not implemented")
    return 0

def ___cxa_end_catch():
    print("___cxa_end_catch not implemented")
    return 

def ___cxa_find_matching_catch_2():
    print("___cxa_find_matching_catch_2 not implemented")
    return 0

def ___cxa_find_matching_catch_3(param0):
    print("___cxa_find_matching_catch_3 not implemented")
    return 0

def ___cxa_find_matching_catch_4(param0,param1):
    print("___cxa_find_matching_catch_4 not implemented")
    return 0

def ___cxa_free_exception(param0):
    print("___cxa_free_exception not implemented")
    return 

def ___cxa_pure_virtual():
    print("___cxa_pure_virtual not implemented")
    return 

def ___cxa_rethrow():
    print("___cxa_rethrow not implemented")
    return 

def ___cxa_throw(param0,param1,param2):
    print("___cxa_throw not implemented")
    return 

def ___lock(param0):
    print("___lock not implemented")
    return 

def ___map_file(param0,param1):
    print("___map_file not implemented")
    return 0

def ___resumeException(param0):
    print("___resumeException not implemented")
    return 

def ___setErrNo(param0):
    print("___setErrNo not implemented")
    return 

def ___syscall10(param0,param1):
    print("___syscall10 not implemented")
    return 0

def ___syscall102(param0,param1):
    print("___syscall102 not implemented")
    return 0

def ___syscall122(param0,param1):
    print("___syscall122 not implemented")
    return 0

def ___syscall140(param0,param1):
    print("___syscall140 not implemented")
    return 0

def ___syscall142(param0,param1):
    print("___syscall142 not implemented")
    return 0

def ___syscall145(param0,param1):
    print("___syscall145 not implemented")
    return 0

def ___syscall146(param0,param1):
    print("___syscall146 not implemented")
    return 0

def ___syscall15(param0,param1):
    print("___syscall15 not implemented")
    return 0

def ___syscall168(param0,param1):
    print("___syscall168 not implemented")
    return 0

def ___syscall183(param0,param1):
    print("___syscall183 not implemented")
    return 0

def ___syscall192(param0,param1):
    print("___syscall192 not implemented")
    return 0

def ___syscall193(param0,param1):
    print("___syscall193 not implemented")
    return 0

def ___syscall194(param0,param1):
    print("___syscall194 not implemented")
    return 0

def ___syscall195(param0,param1):
    print("___syscall195 not implemented")
    return 0

def ___syscall196(param0,param1):
    print("___syscall196 not implemented")
    return 0

def ___syscall197(param0,param1):
    print("___syscall197 not implemented")
    return 0

def ___syscall199(param0,param1):
    print("___syscall199 not implemented")
    return 0

def ___syscall220(param0,param1):
    print("___syscall220 not implemented")
    return 0

def ___syscall221(param0,param1):
    print("___syscall221 not implemented")
    return 0

def ___syscall268(param0,param1):
    print("___syscall268 not implemented")
    return 0

def ___syscall3(param0,param1):
    print("___syscall3 not implemented")
    return 0

def ___syscall33(param0,param1):
    print("___syscall33 not implemented")
    return 0

def ___syscall38(param0,param1):
    print("___syscall38 not implemented")
    return 0

def ___syscall39(param0,param1):
    print("___syscall39 not implemented")
    return 0

def ___syscall4(param0,param1):
    print("___syscall4 not implemented")
    return 0

def ___syscall40(param0,param1):
    print("___syscall40 not implemented")
    return 0

def ___syscall42(param0,param1):
    print("___syscall42 not implemented")
    return 0

def ___syscall5(param0,param1):
    print("___syscall5 not implemented")
    return 0

def ___syscall54(param0,param1):
    print("___syscall54 not implemented")
    return 0

def ___syscall6(param0,param1):
    print("___syscall6 not implemented")
    return 0

def ___syscall63(param0,param1):
    print("___syscall63 not implemented")
    return 0

def ___syscall77(param0,param1):
    print("___syscall77 not implemented")
    return 0

def ___syscall85(param0,param1):
    print("___syscall85 not implemented")
    return 0

def ___syscall91(param0,param1):
    print("___syscall91 not implemented")
    return 0

def ___unlock(param0):
    print("___unlock not implemented")
    return 

def _abort():
    print("_abort not implemented")
    return 

def _atexit(param0):
    print("_atexit not implemented")
    return 0

def _clock():
    print("_clock not implemented")
    return 0

def _clock_getres(param0,param1):
    print("_clock_getres not implemented")
    return 0

def _clock_gettime(param0,param1):
    print("_clock_gettime not implemented")
    return 0

def _difftime(param0,param1):
    print("_difftime not implemented")
    return 0

def _dlclose(param0):
    print("_dlclose not implemented")
    return 0

def _dlopen(param0,param1):
    print("_dlopen not implemented")
    return 0

def _dlsym(param0,param1):
    print("_dlsym not implemented")
    return 0

def _emscripten_asm_const_i(param0):
    print("_emscripten_asm_const_i not implemented")
    return 0

def _emscripten_asm_const_sync_on_main_thread_i(param0):
    print("_emscripten_asm_const_sync_on_main_thread_i not implemented")
    return 0

def _emscripten_cancel_main_loop():
    print("_emscripten_cancel_main_loop not implemented")
    return 

def _emscripten_exit_fullscreen():
    print("_emscripten_exit_fullscreen not implemented")
    return 0

def _emscripten_exit_pointerlock():
    print("_emscripten_exit_pointerlock not implemented")
    return 0

def _emscripten_get_canvas_element_size(param0,param1,param2):
    print("_emscripten_get_canvas_element_size not implemented")
    return 0

def _emscripten_get_fullscreen_status(param0):
    print("_emscripten_get_fullscreen_status not implemented")
    return 0

def _emscripten_get_gamepad_status(param0,param1):
    print("_emscripten_get_gamepad_status not implemented")
    return 0

def _emscripten_get_main_loop_timing(param0,param1):
    print("_emscripten_get_main_loop_timing not implemented")
    return 

def _emscripten_get_now():
    print("_emscripten_get_now not implemented")
    return 0

def _emscripten_get_num_gamepads():
    print("_emscripten_get_num_gamepads not implemented")
    return 0

def _emscripten_has_threading_support():
    print("_emscripten_has_threading_support not implemented")
    return 0

def _emscripten_html5_remove_all_event_listeners():
    print("_emscripten_html5_remove_all_event_listeners not implemented")
    return 

def _emscripten_is_webgl_context_lost(param0):
    print("_emscripten_is_webgl_context_lost not implemented")
    return 0

def _emscripten_log(param0,param1):
    print("_emscripten_log not implemented")
    return 

def _emscripten_longjmp(param0,param1):
    print("_emscripten_longjmp not implemented")
    return 

def _emscripten_memcpy_big(param0,param1,param2):
    print("_emscripten_memcpy_big not implemented")
    return 0

def _emscripten_num_logical_cores():
    print("_emscripten_num_logical_cores not implemented")
    return 0

def _emscripten_request_fullscreen(param0,param1):
    print("_emscripten_request_fullscreen not implemented")
    return 0

def _emscripten_request_pointerlock(param0,param1):
    print("_emscripten_request_pointerlock not implemented")
    return 0

def _emscripten_set_blur_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_blur_callback_on_thread not implemented")
    return 0

def _emscripten_set_canvas_element_size(param0,param1,param2):
    print("_emscripten_set_canvas_element_size not implemented")
    return 0

def _emscripten_set_dblclick_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_dblclick_callback_on_thread not implemented")
    return 0

def _emscripten_set_devicemotion_callback_on_thread(param0,param1,param2,param3):
    print("_emscripten_set_devicemotion_callback_on_thread not implemented")
    return 0

def _emscripten_set_deviceorientation_callback_on_thread(param0,param1,param2,param3):
    print("_emscripten_set_deviceorientation_callback_on_thread not implemented")
    return 0

def _emscripten_set_focus_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_focus_callback_on_thread not implemented")
    return 0

def _emscripten_set_fullscreenchange_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_fullscreenchange_callback_on_thread not implemented")
    return 0

def _emscripten_set_gamepadconnected_callback_on_thread(param0,param1,param2,param3):
    print("_emscripten_set_gamepadconnected_callback_on_thread not implemented")
    return 0

def _emscripten_set_gamepaddisconnected_callback_on_thread(param0,param1,param2,param3):
    print("_emscripten_set_gamepaddisconnected_callback_on_thread not implemented")
    return 0

def _emscripten_set_keydown_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_keydown_callback_on_thread not implemented")
    return 0

def _emscripten_set_keypress_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_keypress_callback_on_thread not implemented")
    return 0

def _emscripten_set_keyup_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_keyup_callback_on_thread not implemented")
    return 0

def _emscripten_set_main_loop(param0,param1,param2):
    print("_emscripten_set_main_loop not implemented")
    return 

def _emscripten_set_main_loop_timing(param0,param1):
    print("_emscripten_set_main_loop_timing not implemented")
    return 0

def _emscripten_set_mousedown_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_mousedown_callback_on_thread not implemented")
    return 0

def _emscripten_set_mousemove_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_mousemove_callback_on_thread not implemented")
    return 0

def _emscripten_set_mouseup_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_mouseup_callback_on_thread not implemented")
    return 0

def _emscripten_set_touchcancel_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_touchcancel_callback_on_thread not implemented")
    return 0

def _emscripten_set_touchend_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_touchend_callback_on_thread not implemented")
    return 0

def _emscripten_set_touchmove_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_touchmove_callback_on_thread not implemented")
    return 0

def _emscripten_set_touchstart_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_touchstart_callback_on_thread not implemented")
    return 0

def _emscripten_set_wheel_callback_on_thread(param0,param1,param2,param3,param4):
    print("_emscripten_set_wheel_callback_on_thread not implemented")
    return 0

def _emscripten_webgl_create_context(param0,param1):
    print("_emscripten_webgl_create_context not implemented")
    return 0

def _emscripten_webgl_destroy_context(param0):
    print("_emscripten_webgl_destroy_context not implemented")
    return 0

def _emscripten_webgl_enable_extension(param0,param1):
    print("_emscripten_webgl_enable_extension not implemented")
    return 0

def _emscripten_webgl_get_current_context():
    print("_emscripten_webgl_get_current_context not implemented")
    return 0

def _emscripten_webgl_init_context_attributes(param0):
    print("_emscripten_webgl_init_context_attributes not implemented")
    return 

def _emscripten_webgl_make_context_current(param0):
    print("_emscripten_webgl_make_context_current not implemented")
    return 0

def _exit(param0):
    print("_exit not implemented")
    return 

def _flock(param0,param1):
    print("_flock not implemented")
    return 0

def _getaddrinfo(param0,param1,param2,param3):
    print("_getaddrinfo not implemented")
    return 0

def _getenv(param0):
    print("_getenv not implemented")
    return 0

def _gethostbyaddr(param0,param1,param2):
    print("_gethostbyaddr not implemented")
    return 0

def _gethostbyname(param0):
    print("_gethostbyname not implemented")
    return 0

def _getnameinfo(param0,param1,param2,param3,param4,param5,param6):
    print("_getnameinfo not implemented")
    return 0

def _getpagesize():
    print("_getpagesize not implemented")
    return 0

def _getpwuid(param0):
    print("_getpwuid not implemented")
    return 0

def _gettimeofday(param0,param1):
    print("_gettimeofday not implemented")
    return 0

def _glActiveTexture(param0):
    print("_glActiveTexture not implemented")
    return 

def _glAttachShader(param0,param1):
    print("_glAttachShader not implemented")
    return 

def _glBeginQuery(param0,param1):
    print("_glBeginQuery not implemented")
    return 

def _glBeginTransformFeedback(param0):
    print("_glBeginTransformFeedback not implemented")
    return 

def _glBindAttribLocation(param0,param1,param2):
    print("_glBindAttribLocation not implemented")
    return 

def _glBindBuffer(param0,param1):
    print("_glBindBuffer not implemented")
    return 

def _glBindBufferBase(param0,param1,param2):
    print("_glBindBufferBase not implemented")
    return 

def _glBindBufferRange(param0,param1,param2,param3,param4):
    print("_glBindBufferRange not implemented")
    return 

def _glBindFramebuffer(param0,param1):
    print("_glBindFramebuffer not implemented")
    return 

def _glBindRenderbuffer(param0,param1):
    print("_glBindRenderbuffer not implemented")
    return 

def _glBindSampler(param0,param1):
    print("_glBindSampler not implemented")
    return 

def _glBindTexture(param0,param1):
    print("_glBindTexture not implemented")
    return 

def _glBindTransformFeedback(param0,param1):
    print("_glBindTransformFeedback not implemented")
    return 

def _glBindVertexArray(param0):
    print("_glBindVertexArray not implemented")
    return 

def _glBlendEquation(param0):
    print("_glBlendEquation not implemented")
    return 

def _glBlendEquationSeparate(param0,param1):
    print("_glBlendEquationSeparate not implemented")
    return 

def _glBlendFuncSeparate(param0,param1,param2,param3):
    print("_glBlendFuncSeparate not implemented")
    return 

def _glBlitFramebuffer(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
    print("_glBlitFramebuffer not implemented")
    return 

def _glBufferData(param0,param1,param2,param3):
    print("_glBufferData not implemented")
    return 

def _glBufferSubData(param0,param1,param2,param3):
    print("_glBufferSubData not implemented")
    return 

def _glCheckFramebufferStatus(param0):
    print("_glCheckFramebufferStatus not implemented")
    return 0

def _glClear(param0):
    print("_glClear not implemented")
    return 

def _glClearBufferfi(param0,param1,param2,param3):
    print("_glClearBufferfi not implemented")
    return 

def _glClearBufferfv(param0,param1,param2):
    print("_glClearBufferfv not implemented")
    return 

def _glClearBufferuiv(param0,param1,param2):
    print("_glClearBufferuiv not implemented")
    return 

def _glClearColor(param0,param1,param2,param3):
    print("_glClearColor not implemented")
    return 

def _glClearDepthf(param0):
    print("_glClearDepthf not implemented")
    return 

def _glClearStencil(param0):
    print("_glClearStencil not implemented")
    return 

def _glColorMask(param0,param1,param2,param3):
    print("_glColorMask not implemented")
    return 

def _glCompileShader(param0):
    print("_glCompileShader not implemented")
    return 

def _glCompressedTexImage2D(param0,param1,param2,param3,param4,param5,param6,param7):
    print("_glCompressedTexImage2D not implemented")
    return 

def _glCompressedTexSubImage2D(param0,param1,param2,param3,param4,param5,param6,param7,param8):
    print("_glCompressedTexSubImage2D not implemented")
    return 

def _glCompressedTexSubImage3D(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
    print("_glCompressedTexSubImage3D not implemented")
    return 

def _glCopyBufferSubData(param0,param1,param2,param3,param4):
    print("_glCopyBufferSubData not implemented")
    return 

def _glCopyTexImage2D(param0,param1,param2,param3,param4,param5,param6,param7):
    print("_glCopyTexImage2D not implemented")
    return 

def _glCopyTexSubImage2D(param0,param1,param2,param3,param4,param5,param6,param7):
    print("_glCopyTexSubImage2D not implemented")
    return 

def _glCreateProgram():
    print("_glCreateProgram not implemented")
    return 0

def _glCreateShader(param0):
    print("_glCreateShader not implemented")
    return 0

def _glCullFace(param0):
    print("_glCullFace not implemented")
    return 

def _glDeleteBuffers(param0,param1):
    print("_glDeleteBuffers not implemented")
    return 

def _glDeleteFramebuffers(param0,param1):
    print("_glDeleteFramebuffers not implemented")
    return 

def _glDeleteProgram(param0):
    print("_glDeleteProgram not implemented")
    return 

def _glDeleteQueries(param0,param1):
    print("_glDeleteQueries not implemented")
    return 

def _glDeleteRenderbuffers(param0,param1):
    print("_glDeleteRenderbuffers not implemented")
    return 

def _glDeleteSamplers(param0,param1):
    print("_glDeleteSamplers not implemented")
    return 

def _glDeleteShader(param0):
    print("_glDeleteShader not implemented")
    return 

def _glDeleteSync(param0):
    print("_glDeleteSync not implemented")
    return 

def _glDeleteTextures(param0,param1):
    print("_glDeleteTextures not implemented")
    return 

def _glDeleteTransformFeedbacks(param0,param1):
    print("_glDeleteTransformFeedbacks not implemented")
    return 

def _glDeleteVertexArrays(param0,param1):
    print("_glDeleteVertexArrays not implemented")
    return 

def _glDepthFunc(param0):
    print("_glDepthFunc not implemented")
    return 

def _glDepthMask(param0):
    print("_glDepthMask not implemented")
    return 

def _glDetachShader(param0,param1):
    print("_glDetachShader not implemented")
    return 

def _glDisable(param0):
    print("_glDisable not implemented")
    return 

def _glDisableVertexAttribArray(param0):
    print("_glDisableVertexAttribArray not implemented")
    return 

def _glDrawArrays(param0,param1,param2):
    print("_glDrawArrays not implemented")
    return 

def _glDrawArraysInstanced(param0,param1,param2,param3):
    print("_glDrawArraysInstanced not implemented")
    return 

def _glDrawBuffers(param0,param1):
    print("_glDrawBuffers not implemented")
    return 

def _glDrawElements(param0,param1,param2,param3):
    print("_glDrawElements not implemented")
    return 

def _glDrawElementsInstanced(param0,param1,param2,param3,param4):
    print("_glDrawElementsInstanced not implemented")
    return 

def _glEnable(param0):
    print("_glEnable not implemented")
    return 

def _glEnableVertexAttribArray(param0):
    print("_glEnableVertexAttribArray not implemented")
    return 

def _glEndQuery(param0):
    print("_glEndQuery not implemented")
    return 

def _glEndTransformFeedback():
    print("_glEndTransformFeedback not implemented")
    return 

def _glFenceSync(param0,param1):
    print("_glFenceSync not implemented")
    return 0

def _glFinish():
    print("_glFinish not implemented")
    return 

def _glFlush():
    print("_glFlush not implemented")
    return 

def _glFlushMappedBufferRange(param0,param1,param2):
    print("_glFlushMappedBufferRange not implemented")
    return 

def _glFramebufferRenderbuffer(param0,param1,param2,param3):
    print("_glFramebufferRenderbuffer not implemented")
    return 

def _glFramebufferTexture2D(param0,param1,param2,param3,param4):
    print("_glFramebufferTexture2D not implemented")
    return 

def _glFramebufferTextureLayer(param0,param1,param2,param3,param4):
    print("_glFramebufferTextureLayer not implemented")
    return 

def _glFrontFace(param0):
    print("_glFrontFace not implemented")
    return 

def _glGenBuffers(param0,param1):
    print("_glGenBuffers not implemented")
    return 

def _glGenFramebuffers(param0,param1):
    print("_glGenFramebuffers not implemented")
    return 

def _glGenQueries(param0,param1):
    print("_glGenQueries not implemented")
    return 

def _glGenRenderbuffers(param0,param1):
    print("_glGenRenderbuffers not implemented")
    return 

def _glGenSamplers(param0,param1):
    print("_glGenSamplers not implemented")
    return 

def _glGenTextures(param0,param1):
    print("_glGenTextures not implemented")
    return 

def _glGenTransformFeedbacks(param0,param1):
    print("_glGenTransformFeedbacks not implemented")
    return 

def _glGenVertexArrays(param0,param1):
    print("_glGenVertexArrays not implemented")
    return 

def _glGenerateMipmap(param0):
    print("_glGenerateMipmap not implemented")
    return 

def _glGetActiveAttrib(param0,param1,param2,param3,param4,param5,param6):
    print("_glGetActiveAttrib not implemented")
    return 

def _glGetActiveUniform(param0,param1,param2,param3,param4,param5,param6):
    print("_glGetActiveUniform not implemented")
    return 

def _glGetActiveUniformBlockName(param0,param1,param2,param3,param4):
    print("_glGetActiveUniformBlockName not implemented")
    return 

def _glGetActiveUniformBlockiv(param0,param1,param2,param3):
    print("_glGetActiveUniformBlockiv not implemented")
    return 

def _glGetActiveUniformsiv(param0,param1,param2,param3,param4):
    print("_glGetActiveUniformsiv not implemented")
    return 

def _glGetAttribLocation(param0,param1):
    print("_glGetAttribLocation not implemented")
    return 0

def _glGetError():
    print("_glGetError not implemented")
    return 0

def _glGetFramebufferAttachmentParameteriv(param0,param1,param2,param3):
    print("_glGetFramebufferAttachmentParameteriv not implemented")
    return 

def _glGetIntegeri_v(param0,param1,param2):
    print("_glGetIntegeri_v not implemented")
    return 

def _glGetIntegerv(param0,param1):
    print("_glGetIntegerv not implemented")
    return 

def _glGetInternalformativ(param0,param1,param2,param3,param4):
    print("_glGetInternalformativ not implemented")
    return 

def _glGetProgramBinary(param0,param1,param2,param3,param4):
    print("_glGetProgramBinary not implemented")
    return 

def _glGetProgramInfoLog(param0,param1,param2,param3):
    print("_glGetProgramInfoLog not implemented")
    return 

def _glGetProgramiv(param0,param1,param2):
    print("_glGetProgramiv not implemented")
    return 

def _glGetRenderbufferParameteriv(param0,param1,param2):
    print("_glGetRenderbufferParameteriv not implemented")
    return 

def _glGetShaderInfoLog(param0,param1,param2,param3):
    print("_glGetShaderInfoLog not implemented")
    return 

def _glGetShaderPrecisionFormat(param0,param1,param2,param3):
    print("_glGetShaderPrecisionFormat not implemented")
    return 

def _glGetShaderSource(param0,param1,param2,param3):
    print("_glGetShaderSource not implemented")
    return 

def _glGetShaderiv(param0,param1,param2):
    print("_glGetShaderiv not implemented")
    return 

def _glGetString(param0):
    print("_glGetString not implemented")
    return 0

def _glGetStringi(param0,param1):
    print("_glGetStringi not implemented")
    return 0

def _glGetTexParameteriv(param0,param1,param2):
    print("_glGetTexParameteriv not implemented")
    return 

def _glGetUniformBlockIndex(param0,param1):
    print("_glGetUniformBlockIndex not implemented")
    return 0

def _glGetUniformIndices(param0,param1,param2,param3):
    print("_glGetUniformIndices not implemented")
    return 

def _glGetUniformLocation(param0,param1):
    print("_glGetUniformLocation not implemented")
    return 0

def _glGetUniformiv(param0,param1,param2):
    print("_glGetUniformiv not implemented")
    return 

def _glGetVertexAttribiv(param0,param1,param2):
    print("_glGetVertexAttribiv not implemented")
    return 

def _glInvalidateFramebuffer(param0,param1,param2):
    print("_glInvalidateFramebuffer not implemented")
    return 

def _glIsEnabled(param0):
    print("_glIsEnabled not implemented")
    return 0

def _glIsVertexArray(param0):
    print("_glIsVertexArray not implemented")
    return 0

def _glLinkProgram(param0):
    print("_glLinkProgram not implemented")
    return 

def _glMapBufferRange(param0,param1,param2,param3):
    print("_glMapBufferRange not implemented")
    return 0

def _glPixelStorei(param0,param1):
    print("_glPixelStorei not implemented")
    return 

def _glPolygonOffset(param0,param1):
    print("_glPolygonOffset not implemented")
    return 

def _glProgramBinary(param0,param1,param2,param3):
    print("_glProgramBinary not implemented")
    return 

def _glProgramParameteri(param0,param1,param2):
    print("_glProgramParameteri not implemented")
    return 

def _glReadBuffer(param0):
    print("_glReadBuffer not implemented")
    return 

def _glReadPixels(param0,param1,param2,param3,param4,param5,param6):
    print("_glReadPixels not implemented")
    return 

def _glRenderbufferStorage(param0,param1,param2,param3):
    print("_glRenderbufferStorage not implemented")
    return 

def _glRenderbufferStorageMultisample(param0,param1,param2,param3,param4):
    print("_glRenderbufferStorageMultisample not implemented")
    return 

def _glSamplerParameteri(param0,param1,param2):
    print("_glSamplerParameteri not implemented")
    return 

def _glScissor(param0,param1,param2,param3):
    print("_glScissor not implemented")
    return 

def _glShaderSource(param0,param1,param2,param3):
    print("_glShaderSource not implemented")
    return 

def _glStencilFuncSeparate(param0,param1,param2,param3):
    print("_glStencilFuncSeparate not implemented")
    return 

def _glStencilMask(param0):
    print("_glStencilMask not implemented")
    return 

def _glStencilOpSeparate(param0,param1,param2,param3):
    print("_glStencilOpSeparate not implemented")
    return 

def _glTexImage2D(param0,param1,param2,param3,param4,param5,param6,param7,param8):
    print("_glTexImage2D not implemented")
    return 

def _glTexImage3D(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
    print("_glTexImage3D not implemented")
    return 

def _glTexParameterf(param0,param1,param2):
    print("_glTexParameterf not implemented")
    return 

def _glTexParameteri(param0,param1,param2):
    print("_glTexParameteri not implemented")
    return 

def _glTexParameteriv(param0,param1,param2):
    print("_glTexParameteriv not implemented")
    return 

def _glTexStorage2D(param0,param1,param2,param3,param4):
    print("_glTexStorage2D not implemented")
    return 

def _glTexStorage3D(param0,param1,param2,param3,param4,param5):
    print("_glTexStorage3D not implemented")
    return 

def _glTexSubImage2D(param0,param1,param2,param3,param4,param5,param6,param7,param8):
    print("_glTexSubImage2D not implemented")
    return 

def _glTexSubImage3D(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
    print("_glTexSubImage3D not implemented")
    return 

def _glTransformFeedbackVaryings(param0,param1,param2,param3):
    print("_glTransformFeedbackVaryings not implemented")
    return 

def _glUniform1fv(param0,param1,param2):
    print("_glUniform1fv not implemented")
    return 

def _glUniform1i(param0,param1):
    print("_glUniform1i not implemented")
    return 

def _glUniform1iv(param0,param1,param2):
    print("_glUniform1iv not implemented")
    return 

def _glUniform1uiv(param0,param1,param2):
    print("_glUniform1uiv not implemented")
    return 

def _glUniform2fv(param0,param1,param2):
    print("_glUniform2fv not implemented")
    return 

def _glUniform2iv(param0,param1,param2):
    print("_glUniform2iv not implemented")
    return 

def _glUniform2uiv(param0,param1,param2):
    print("_glUniform2uiv not implemented")
    return 

def _glUniform3fv(param0,param1,param2):
    print("_glUniform3fv not implemented")
    return 

def _glUniform3iv(param0,param1,param2):
    print("_glUniform3iv not implemented")
    return 

def _glUniform3uiv(param0,param1,param2):
    print("_glUniform3uiv not implemented")
    return 

def _glUniform4fv(param0,param1,param2):
    print("_glUniform4fv not implemented")
    return 

def _glUniform4iv(param0,param1,param2):
    print("_glUniform4iv not implemented")
    return 

def _glUniform4uiv(param0,param1,param2):
    print("_glUniform4uiv not implemented")
    return 

def _glUniformBlockBinding(param0,param1,param2):
    print("_glUniformBlockBinding not implemented")
    return 

def _glUniformMatrix3fv(param0,param1,param2,param3):
    print("_glUniformMatrix3fv not implemented")
    return 

def _glUniformMatrix4fv(param0,param1,param2,param3):
    print("_glUniformMatrix4fv not implemented")
    return 

def _glUnmapBuffer(param0):
    print("_glUnmapBuffer not implemented")
    return 0

def _glUseProgram(param0):
    print("_glUseProgram not implemented")
    return 

def _glValidateProgram(param0):
    print("_glValidateProgram not implemented")
    return 

def _glVertexAttrib4f(param0,param1,param2,param3,param4):
    print("_glVertexAttrib4f not implemented")
    return 

def _glVertexAttrib4fv(param0,param1):
    print("_glVertexAttrib4fv not implemented")
    return 

def _glVertexAttribIPointer(param0,param1,param2,param3,param4):
    print("_glVertexAttribIPointer not implemented")
    return 

def _glVertexAttribPointer(param0,param1,param2,param3,param4,param5):
    print("_glVertexAttribPointer not implemented")
    return 

def _glViewport(param0,param1,param2,param3):
    print("_glViewport not implemented")
    return 

def _gmtime(param0):
    print("_gmtime not implemented")
    return 0

def _inet_addr(param0):
    print("_inet_addr not implemented")
    return 0

def _llvm_eh_typeid_for(param0):
    print("_llvm_eh_typeid_for not implemented")
    return 0

def _llvm_exp2_f32(param0):
    print("_llvm_exp2_f32 not implemented")
    return 0

def _llvm_log10_f32(param0):
    print("_llvm_log10_f32 not implemented")
    return 0

def _llvm_log10_f64(param0):
    print("_llvm_log10_f64 not implemented")
    return 0

def _llvm_log2_f32(param0):
    print("_llvm_log2_f32 not implemented")
    return 0

def _llvm_trap():
    print("_llvm_trap not implemented")
    return 

def _llvm_trunc_f32(param0):
    print("_llvm_trunc_f32 not implemented")
    return 0

def _localtime(param0):
    print("_localtime not implemented")
    return 0

def _longjmp(param0,param1):
    print("_longjmp not implemented")
    return 

def _mktime(param0):
    print("_mktime not implemented")
    return 0

def _pthread_cond_destroy(param0):
    print("_pthread_cond_destroy not implemented")
    return 0

def _pthread_cond_init(param0,param1):
    print("_pthread_cond_init not implemented")
    return 0

def _pthread_cond_timedwait(param0,param1,param2):
    print("_pthread_cond_timedwait not implemented")
    return 0

def _pthread_cond_wait(param0,param1):
    print("_pthread_cond_wait not implemented")
    return 0

def _pthread_getspecific(param0):
    print("_pthread_getspecific not implemented")
    return 0

def _pthread_key_create(param0,param1):
    print("_pthread_key_create not implemented")
    return 0

def _pthread_key_delete(param0):
    print("_pthread_key_delete not implemented")
    return 0

def _pthread_mutex_destroy(param0):
    print("_pthread_mutex_destroy not implemented")
    return 0

def _pthread_mutex_init(param0,param1):
    print("_pthread_mutex_init not implemented")
    return 0

def _pthread_mutexattr_destroy(param0):
    print("_pthread_mutexattr_destroy not implemented")
    return 0

def _pthread_mutexattr_init(param0):
    print("_pthread_mutexattr_init not implemented")
    return 0

def _pthread_mutexattr_setprotocol(param0,param1):
    print("_pthread_mutexattr_setprotocol not implemented")
    return 0

def _pthread_mutexattr_settype(param0,param1):
    print("_pthread_mutexattr_settype not implemented")
    return 0

def _pthread_once(param0,param1):
    print("_pthread_once not implemented")
    return 0

def _pthread_setspecific(param0,param1):
    print("_pthread_setspecific not implemented")
    return 0

def _sched_yield():
    print("_sched_yield not implemented")
    return 0

def _setenv(param0,param1,param2):
    print("_setenv not implemented")
    return 0

def _sigaction(param0,param1,param2):
    print("_sigaction not implemented")
    return 0

def _sigemptyset(param0):
    print("_sigemptyset not implemented")
    return 0

def _strftime(param0,param1,param2,param3):
    print("_strftime not implemented")
    return 0

def _sysconf(param0):
    print("_sysconf not implemented")
    return 0

def _time(param0):
    print("_time not implemented")
    return 0

def _unsetenv(param0):
    print("_unsetenv not implemented")
    return 0

def _utime(param0,param1):
    print("_utime not implemented")
    return 0

def f64_rem(param0,param1):
    print("f64_rem not implemented")
    return 0

def invoke_iiiiij(param0,param1,param2,param3,param4,param5,param6):
    print("invoke_iiiiij not implemented")
    return 0

def invoke_iiiijii(param0,param1,param2,param3,param4,param5,param6,param7):
    print("invoke_iiiijii not implemented")
    return 0

def invoke_iiiijjii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
    print("invoke_iiiijjii not implemented")
    return 0

def invoke_iiiji(param0,param1,param2,param3,param4,param5):
    print("invoke_iiiji not implemented")
    return 0

def invoke_iiijiii(param0,param1,param2,param3,param4,param5,param6,param7):
    print("invoke_iiijiii not implemented")
    return 0

def invoke_iij(param0,param1,param2,param3):
    print("invoke_iij not implemented")
    return 0

def invoke_iiji(param0,param1,param2,param3,param4):
    print("invoke_iiji not implemented")
    return 0

def invoke_iijii(param0,param1,param2,param3,param4,param5):
    print("invoke_iijii not implemented")
    return 0

def invoke_ijii(param0,param1,param2,param3,param4):
    print("invoke_ijii not implemented")
    return 0

def invoke_j(param0):
    print("invoke_j not implemented")
    return 0

def invoke_jdi(param0,param1,param2):
    print("invoke_jdi not implemented")
    return 0

def invoke_ji(param0,param1):
    print("invoke_ji not implemented")
    return 0

def invoke_jii(param0,param1,param2):
    print("invoke_jii not implemented")
    return 0

def invoke_jiii(param0,param1,param2,param3):
    print("invoke_jiii not implemented")
    return 0

def invoke_jiiii(param0,param1,param2,param3,param4):
    print("invoke_jiiii not implemented")
    return 0

def invoke_jiiiii(param0,param1,param2,param3,param4,param5):
    print("invoke_jiiiii not implemented")
    return 0

def invoke_jiiiiiiiiii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
    print("invoke_jiiiiiiiiii not implemented")
    return 0

def invoke_jiiij(param0,param1,param2,param3,param4,param5):
    print("invoke_jiiij not implemented")
    return 0

def invoke_jiiji(param0,param1,param2,param3,param4,param5):
    print("invoke_jiiji not implemented")
    return 0

def invoke_jiji(param0,param1,param2,param3,param4):
    print("invoke_jiji not implemented")
    return 0

def invoke_jijii(param0,param1,param2,param3,param4,param5):
    print("invoke_jijii not implemented")
    return 0

def invoke_jijiii(param0,param1,param2,param3,param4,param5,param6):
    print("invoke_jijiii not implemented")
    return 0

def invoke_jijj(param0,param1,param2,param3,param4,param5):
    print("invoke_jijj not implemented")
    return 0

def invoke_jji(param0,param1,param2,param3):
    print("invoke_jji not implemented")
    return 0

def invoke_viiiiiiifjjfii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,param11,param12,param13,param14,param15):
    print("invoke_viiiiiiifjjfii not implemented")
    return 

def invoke_viiiijiiii(param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
    print("invoke_viiiijiiii not implemented")
    return 

def invoke_viiij(param0,param1,param2,param3,param4,param5):
    print("invoke_viiij not implemented")
    return 

def invoke_viiiji(param0,param1,param2,param3,param4,param5,param6):
    print("invoke_viiiji not implemented")
    return 

def invoke_viij(param0,param1,param2,param3,param4):
    print("invoke_viij not implemented")
    return 

def invoke_viiji(param0,param1,param2,param3,param4,param5):
    print("invoke_viiji not implemented")
    return 

def invoke_viijji(param0,param1,param2,param3,param4,param5,param6,param7):
    print("invoke_viijji not implemented")
    return 

def invoke_viji(param0,param1,param2,param3,param4):
    print("invoke_viji not implemented")
    return 

def invoke_vijii(param0,param1,param2,param3,param4,param5):
    print("invoke_vijii not implemented")
    return 

def ___atomic_fetch_add_8(param0,param1,param2,param3):
    print("___atomic_fetch_add_8 not implemented")
    return 0

def _glClientWaitSync(param0,param1,param2,param3):
    print("_glClientWaitSync not implemented")
    return 0

def pow(param0, param1):
    return pow(param0, param1)

import_object = {
    "env": {
        "abort": Func(store, FuncType([ValType.i32()], []), abort),
        "enlargeMemory": Func(store, FuncType([], [ValType.i32()]), enlargeMemory),
        "getTotalMemory": Func(store, FuncType([], [ValType.i32()]), getTotalMemory),
        "abortOnCannotGrowMemory": Func(store, FuncType([], [ValType.i32()]), abortOnCannotGrowMemory),
        "invoke_dddi": Func(store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.i32()], [ValType.f64()]), invoke_dddi),
        "invoke_dii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), invoke_dii),
        "invoke_diii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), invoke_diii),
        "invoke_diiid": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64()], [ValType.f64()]), invoke_diiid),
        "invoke_diiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), invoke_diiii),
        "invoke_ffffi": Func(store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32()], [ValType.f64()]), invoke_ffffi),
        "invoke_fffi": Func(store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.i32()], [ValType.f64()]), invoke_fffi),
        "invoke_fi": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.f64()]), invoke_fi),
        "invoke_fii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), invoke_fii),
        "invoke_fiifi": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], [ValType.f64()]), invoke_fiifi),
        "invoke_fiifii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], [ValType.f64()]), invoke_fiifii),
        "invoke_fiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), invoke_fiii),
        "invoke_fiiif": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64()], [ValType.f64()]), invoke_fiiif),
        "invoke_fiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), invoke_fiiii),
        "invoke_i": Func(store, FuncType([ValType.i32()], [ValType.i32()]), invoke_i),
        "invoke_ifi": Func(store, FuncType([ValType.i32(),ValType.f64(),ValType.i32()], [ValType.i32()]), invoke_ifi),
        "invoke_ii": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_ii),
        "invoke_iifii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iifii),
        "invoke_iii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iii),
        "invoke_iiifi": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], [ValType.i32()]), invoke_iiifi),
        "invoke_iiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiii),
        "invoke_iiiifii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiifii),
        "invoke_iiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiii),
        "invoke_iiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiiii),
        "invoke_iiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiiiii),
        "invoke_iiiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiiiiii),
        "invoke_iiiiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiiiiiii),
        "invoke_iiiiiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiiiiiiii),
        "invoke_iiiiiiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiiiiiiiii),
        "invoke_v": Func(store, FuncType([ValType.i32()], []), invoke_v),
        "invoke_vi": Func(store, FuncType([ValType.i32(),ValType.i32()], []), invoke_vi),
        "invoke_vidiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_vidiii),
        "invoke_vifffi": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32()], []), invoke_vifffi),
        "invoke_vifi": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), invoke_vifi),
        "invoke_vifii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), invoke_vifii),
        "invoke_vii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_vii),
        "invoke_viidi": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), invoke_viidi),
        "invoke_viidii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), invoke_viidii),
        "invoke_viiff": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64()], []), invoke_viiff),
        "invoke_viiffi": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.i32()], []), invoke_viiffi),
        "invoke_viifi": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), invoke_viifi),
        "invoke_viifii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), invoke_viifii),
        "invoke_viii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viii),
        "invoke_viiif": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64()], []), invoke_viiif),
        "invoke_viiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiii),
        "invoke_viiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiiii),
        "invoke_viiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiiiii),
        "invoke_viiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiiiiii),
        "invoke_viiiiiiifddfii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32(),ValType.i32()], []), invoke_viiiiiiifddfii),
        "invoke_viiiiiiiffffii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32(),ValType.i32()], []), invoke_viiiiiiiffffii),
        "invoke_viiiiiiifiifii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), invoke_viiiiiiifiifii),
        "invoke_viiiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiiiiiii),
        "invoke_viiiiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiiiiiiii),
        "invoke_viiiiiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiiiiiiiii),
        "_ES_AddEventHandler": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _ES_AddEventHandler),
        "_ES_Close": Func(store, FuncType([ValType.i32()], []), _ES_Close),
        "_ES_Create": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _ES_Create),
        "_ES_IsSupported": Func(store, FuncType([], [ValType.i32()]), _ES_IsSupported),
        "_ES_Release": Func(store, FuncType([ValType.i32()], []), _ES_Release),
        "_GetInputFieldSelectionEnd": Func(store, FuncType([], [ValType.i32()]), _GetInputFieldSelectionEnd),
        "_GetInputFieldSelectionStart": Func(store, FuncType([], [ValType.i32()]), _GetInputFieldSelectionStart),
        "_GetInputFieldValue": Func(store, FuncType([], [ValType.i32()]), _GetInputFieldValue),
        "_HideInputField": Func(store, FuncType([], []), _HideInputField),
        "_IsInputFieldActive": Func(store, FuncType([], [ValType.i32()]), _IsInputFieldActive),
        "_JS_Cursor_SetImage": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_Cursor_SetImage),
        "_JS_Cursor_SetShow": Func(store, FuncType([ValType.i32()], []), _JS_Cursor_SetShow),
        "_JS_Eval_ClearInterval": Func(store, FuncType([ValType.i32()], []), _JS_Eval_ClearInterval),
        "_JS_Eval_OpenURL": Func(store, FuncType([ValType.i32()], []), _JS_Eval_OpenURL),
        "_JS_Eval_SetInterval": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_Eval_SetInterval),
        "_JS_FileSystem_Initialize": Func(store, FuncType([], []), _JS_FileSystem_Initialize),
        "_JS_FileSystem_Sync": Func(store, FuncType([], []), _JS_FileSystem_Sync),
        "_JS_Log_Dump": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_Log_Dump),
        "_JS_Log_StackTrace": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_Log_StackTrace),
        "_JS_Sound_Create_Channel": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_Sound_Create_Channel),
        "_JS_Sound_GetLength": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Sound_GetLength),
        "_JS_Sound_GetLoadState": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Sound_GetLoadState),
        "_JS_Sound_Init": Func(store, FuncType([], []), _JS_Sound_Init),
        "_JS_Sound_Load": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_Sound_Load),
        "_JS_Sound_Load_PCM": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_Sound_Load_PCM),
        "_JS_Sound_Play": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64()], []), _JS_Sound_Play),
        "_JS_Sound_ReleaseInstance": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Sound_ReleaseInstance),
        "_JS_Sound_ResumeIfNeeded": Func(store, FuncType([], []), _JS_Sound_ResumeIfNeeded),
        "_JS_Sound_Set3D": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_Sound_Set3D),
        "_JS_Sound_SetListenerOrientation": Func(store, FuncType([ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64()], []), _JS_Sound_SetListenerOrientation),
        "_JS_Sound_SetListenerPosition": Func(store, FuncType([ValType.f64(),ValType.f64(),ValType.f64()], []), _JS_Sound_SetListenerPosition),
        "_JS_Sound_SetLoop": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_Sound_SetLoop),
        "_JS_Sound_SetLoopPoints": Func(store, FuncType([ValType.i32(),ValType.f64(),ValType.f64()], []), _JS_Sound_SetLoopPoints),
        "_JS_Sound_SetPaused": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_Sound_SetPaused),
        "_JS_Sound_SetPitch": Func(store, FuncType([ValType.i32(),ValType.f64()], []), _JS_Sound_SetPitch),
        "_JS_Sound_SetPosition": Func(store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64()], []), _JS_Sound_SetPosition),
        "_JS_Sound_SetVolume": Func(store, FuncType([ValType.i32(),ValType.f64()], []), _JS_Sound_SetVolume),
        "_JS_Sound_Stop": Func(store, FuncType([ValType.i32(),ValType.f64()], []), _JS_Sound_Stop),
        "_JS_SystemInfo_GetBrowserName": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_SystemInfo_GetBrowserName),
        "_JS_SystemInfo_GetBrowserVersionString": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_SystemInfo_GetBrowserVersionString),
        "_JS_SystemInfo_GetCanvasClientSize": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_SystemInfo_GetCanvasClientSize),
        "_JS_SystemInfo_GetDocumentURL": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_SystemInfo_GetDocumentURL),
        "_JS_SystemInfo_GetGPUInfo": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_SystemInfo_GetGPUInfo),
        "_JS_SystemInfo_GetLanguage": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_SystemInfo_GetLanguage),
        "_JS_SystemInfo_GetMemory": Func(store, FuncType([], [ValType.i32()]), _JS_SystemInfo_GetMemory),
        "_JS_SystemInfo_GetOS": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_SystemInfo_GetOS),
        "_JS_SystemInfo_GetPreferredDevicePixelRatio": Func(store, FuncType([], [ValType.f64()]), _JS_SystemInfo_GetPreferredDevicePixelRatio),
        "_JS_SystemInfo_GetScreenSize": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_SystemInfo_GetScreenSize),
        "_JS_SystemInfo_GetStreamingAssetsURL": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_SystemInfo_GetStreamingAssetsURL),
        "_JS_SystemInfo_HasCursorLock": Func(store, FuncType([], [ValType.i32()]), _JS_SystemInfo_HasCursorLock),
        "_JS_SystemInfo_HasFullscreen": Func(store, FuncType([], [ValType.i32()]), _JS_SystemInfo_HasFullscreen),
        "_JS_SystemInfo_HasWebGL": Func(store, FuncType([], [ValType.i32()]), _JS_SystemInfo_HasWebGL),
        "_JS_SystemInfo_IsMobile": Func(store, FuncType([], [ValType.i32()]), _JS_SystemInfo_IsMobile),
        "_JS_Video_CanPlayFormat": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Video_CanPlayFormat),
        "_JS_Video_Create": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Video_Create),
        "_JS_Video_Destroy": Func(store, FuncType([ValType.i32()], []), _JS_Video_Destroy),
        "_JS_Video_Duration": Func(store, FuncType([ValType.i32()], [ValType.f64()]), _JS_Video_Duration),
        "_JS_Video_EnableAudioTrack": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_Video_EnableAudioTrack),
        "_JS_Video_GetAudioLanguageCode": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_Video_GetAudioLanguageCode),
        "_JS_Video_GetNumAudioTracks": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Video_GetNumAudioTracks),
        "_JS_Video_Height": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Video_Height),
        "_JS_Video_IsPlaying": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Video_IsPlaying),
        "_JS_Video_IsReady": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Video_IsReady),
        "_JS_Video_Pause": Func(store, FuncType([ValType.i32()], []), _JS_Video_Pause),
        "_JS_Video_Play": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_Video_Play),
        "_JS_Video_Seek": Func(store, FuncType([ValType.i32(),ValType.f64()], []), _JS_Video_Seek),
        "_JS_Video_SetEndedHandler": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_Video_SetEndedHandler),
        "_JS_Video_SetErrorHandler": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_Video_SetErrorHandler),
        "_JS_Video_SetLoop": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_Video_SetLoop),
        "_JS_Video_SetMute": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_Video_SetMute),
        "_JS_Video_SetPlaybackRate": Func(store, FuncType([ValType.i32(),ValType.f64()], []), _JS_Video_SetPlaybackRate),
        "_JS_Video_SetReadyHandler": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_Video_SetReadyHandler),
        "_JS_Video_SetSeekedOnceHandler": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_Video_SetSeekedOnceHandler),
        "_JS_Video_SetVolume": Func(store, FuncType([ValType.i32(),ValType.f64()], []), _JS_Video_SetVolume),
        "_JS_Video_Time": Func(store, FuncType([ValType.i32()], [ValType.f64()]), _JS_Video_Time),
        "_JS_Video_UpdateToTexture": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_Video_UpdateToTexture),
        "_JS_Video_Width": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_Video_Width),
        "_JS_WebCamVideo_CanPlay": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_WebCamVideo_CanPlay),
        "_JS_WebCamVideo_GetDeviceName": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_WebCamVideo_GetDeviceName),
        "_JS_WebCamVideo_GetNativeHeight": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_WebCamVideo_GetNativeHeight),
        "_JS_WebCamVideo_GetNativeWidth": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _JS_WebCamVideo_GetNativeWidth),
        "_JS_WebCamVideo_GetNumDevices": Func(store, FuncType([], [ValType.i32()]), _JS_WebCamVideo_GetNumDevices),
        "_JS_WebCamVideo_GrabFrame": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_WebCamVideo_GrabFrame),
        "_JS_WebCamVideo_Start": Func(store, FuncType([ValType.i32()], []), _JS_WebCamVideo_Start),
        "_JS_WebCamVideo_Stop": Func(store, FuncType([ValType.i32()], []), _JS_WebCamVideo_Stop),
        "_JS_WebCam_IsSupported": Func(store, FuncType([], [ValType.i32()]), _JS_WebCam_IsSupported),
        "_JS_WebRequest_Abort": Func(store, FuncType([ValType.i32()], []), _JS_WebRequest_Abort),
        "_JS_WebRequest_Create": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_WebRequest_Create),
        "_JS_WebRequest_GetResponseHeaders": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _JS_WebRequest_GetResponseHeaders),
        "_JS_WebRequest_Release": Func(store, FuncType([ValType.i32()], []), _JS_WebRequest_Release),
        "_JS_WebRequest_Send": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_WebRequest_Send),
        "_JS_WebRequest_SetProgressHandler": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_WebRequest_SetProgressHandler),
        "_JS_WebRequest_SetRequestHeader": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_WebRequest_SetRequestHeader),
        "_JS_WebRequest_SetResponseHandler": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _JS_WebRequest_SetResponseHandler),
        "_JS_WebRequest_SetTimeout": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _JS_WebRequest_SetTimeout),
        "_NativeCall": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _NativeCall),
        "_SetInputFieldSelection": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _SetInputFieldSelection),
        "_ShowInputField": Func(store, FuncType([ValType.i32()], []), _ShowInputField),
        "_WS_Close": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _WS_Close),
        "_WS_Create": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _WS_Create),
        "_WS_GetBufferedAmount": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _WS_GetBufferedAmount),
        "_WS_GetState": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _WS_GetState),
        "_WS_Release": Func(store, FuncType([ValType.i32()], []), _WS_Release),
        "_WS_Send_Binary": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _WS_Send_Binary),
        "_WS_Send_String": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _WS_Send_String),
        "_XHR_Abort": Func(store, FuncType([ValType.i32()], []), _XHR_Abort),
        "_XHR_Create": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _XHR_Create),
        "_XHR_GetResponseHeaders": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _XHR_GetResponseHeaders),
        "_XHR_GetStatusLine": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _XHR_GetStatusLine),
        "_XHR_Release": Func(store, FuncType([ValType.i32()], []), _XHR_Release),
        "_XHR_Send": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _XHR_Send),
        "_XHR_SetLoglevel": Func(store, FuncType([ValType.i32()], []), _XHR_SetLoglevel),
        "_XHR_SetProgressHandler": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _XHR_SetProgressHandler),
        "_XHR_SetRequestHeader": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _XHR_SetRequestHeader),
        "_XHR_SetResponseHandler": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _XHR_SetResponseHandler),
        "_XHR_SetTimeout": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _XHR_SetTimeout),
        "___buildEnvironment": Func(store, FuncType([ValType.i32()], []), ___buildEnvironment),
        "___cxa_allocate_exception": Func(store, FuncType([ValType.i32()], [ValType.i32()]), ___cxa_allocate_exception),
        "___cxa_begin_catch": Func(store, FuncType([ValType.i32()], [ValType.i32()]), ___cxa_begin_catch),
        "___cxa_end_catch": Func(store, FuncType([], []), ___cxa_end_catch),
        "___cxa_find_matching_catch_2": Func(store, FuncType([], [ValType.i32()]), ___cxa_find_matching_catch_2),
        "___cxa_find_matching_catch_3": Func(store, FuncType([ValType.i32()], [ValType.i32()]), ___cxa_find_matching_catch_3),
        "___cxa_find_matching_catch_4": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___cxa_find_matching_catch_4),
        "___cxa_free_exception": Func(store, FuncType([ValType.i32()], []), ___cxa_free_exception),
        "___cxa_pure_virtual": Func(store, FuncType([], []), ___cxa_pure_virtual),
        "___cxa_rethrow": Func(store, FuncType([], []), ___cxa_rethrow),
        "___cxa_throw": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), ___cxa_throw),
        "___lock": Func(store, FuncType([ValType.i32()], []), ___lock),
        "___map_file": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___map_file),
        "___resumeException": Func(store, FuncType([ValType.i32()], []), ___resumeException),
        "___setErrNo": Func(store, FuncType([ValType.i32()], []), ___setErrNo),
        "___syscall10": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall10),
        "___syscall102": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall102),
        "___syscall122": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall122),
        "___syscall140": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall140),
        "___syscall142": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall142),
        "___syscall145": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall145),
        "___syscall146": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall146),
        "___syscall15": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall15),
        "___syscall168": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall168),
        "___syscall183": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall183),
        "___syscall192": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall192),
        "___syscall193": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall193),
        "___syscall194": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall194),
        "___syscall195": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall195),
        "___syscall196": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall196),
        "___syscall197": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall197),
        "___syscall199": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall199),
        "___syscall220": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall220),
        "___syscall221": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall221),
        "___syscall268": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall268),
        "___syscall3": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall3),
        "___syscall33": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall33),
        "___syscall38": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall38),
        "___syscall39": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall39),
        "___syscall4": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall4),
        "___syscall40": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall40),
        "___syscall42": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall42),
        "___syscall5": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall5),
        "___syscall54": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall54),
        "___syscall6": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall6),
        "___syscall63": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall63),
        "___syscall77": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall77),
        "___syscall85": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall85),
        "___syscall91": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), ___syscall91),
        "___unlock": Func(store, FuncType([ValType.i32()], []), ___unlock),
        "_abort": Func(store, FuncType([], []), _abort),
        "_atexit": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _atexit),
        "_clock": Func(store, FuncType([], [ValType.i32()]), _clock),
        "_clock_getres": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _clock_getres),
        "_clock_gettime": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _clock_gettime),
        "_difftime": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.f64()]), _difftime),
        "_dlclose": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _dlclose),
        "_dlopen": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _dlopen),
        "_dlsym": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _dlsym),
        "_emscripten_asm_const_i": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _emscripten_asm_const_i),
        "_emscripten_asm_const_sync_on_main_thread_i": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _emscripten_asm_const_sync_on_main_thread_i),
        "_emscripten_cancel_main_loop": Func(store, FuncType([], []), _emscripten_cancel_main_loop),
        "_emscripten_exit_fullscreen": Func(store, FuncType([], [ValType.i32()]), _emscripten_exit_fullscreen),
        "_emscripten_exit_pointerlock": Func(store, FuncType([], [ValType.i32()]), _emscripten_exit_pointerlock),
        "_emscripten_get_canvas_element_size": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_get_canvas_element_size),
        "_emscripten_get_fullscreen_status": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _emscripten_get_fullscreen_status),
        "_emscripten_get_gamepad_status": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_get_gamepad_status),
        "_emscripten_get_main_loop_timing": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _emscripten_get_main_loop_timing),
        "_emscripten_get_now": Func(store, FuncType([], [ValType.f64()]), _emscripten_get_now),
        "_emscripten_get_num_gamepads": Func(store, FuncType([], [ValType.i32()]), _emscripten_get_num_gamepads),
        "_emscripten_has_threading_support": Func(store, FuncType([], [ValType.i32()]), _emscripten_has_threading_support),
        "_emscripten_html5_remove_all_event_listeners": Func(store, FuncType([], []), _emscripten_html5_remove_all_event_listeners),
        "_emscripten_is_webgl_context_lost": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _emscripten_is_webgl_context_lost),
        "_emscripten_log": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _emscripten_log),
        "_emscripten_longjmp": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _emscripten_longjmp),
        "_emscripten_memcpy_big": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_memcpy_big),
        "_emscripten_num_logical_cores": Func(store, FuncType([], [ValType.i32()]), _emscripten_num_logical_cores),
        "_emscripten_request_fullscreen": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_request_fullscreen),
        "_emscripten_request_pointerlock": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_request_pointerlock),
        "_emscripten_set_blur_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_blur_callback_on_thread),
        "_emscripten_set_canvas_element_size": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_canvas_element_size),
        "_emscripten_set_dblclick_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_dblclick_callback_on_thread),
        "_emscripten_set_devicemotion_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_devicemotion_callback_on_thread),
        "_emscripten_set_deviceorientation_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_deviceorientation_callback_on_thread),
        "_emscripten_set_focus_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_focus_callback_on_thread),
        "_emscripten_set_fullscreenchange_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_fullscreenchange_callback_on_thread),
        "_emscripten_set_gamepadconnected_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_gamepadconnected_callback_on_thread),
        "_emscripten_set_gamepaddisconnected_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_gamepaddisconnected_callback_on_thread),
        "_emscripten_set_keydown_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_keydown_callback_on_thread),
        "_emscripten_set_keypress_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_keypress_callback_on_thread),
        "_emscripten_set_keyup_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_keyup_callback_on_thread),
        "_emscripten_set_main_loop": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _emscripten_set_main_loop),
        "_emscripten_set_main_loop_timing": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_main_loop_timing),
        "_emscripten_set_mousedown_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_mousedown_callback_on_thread),
        "_emscripten_set_mousemove_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_mousemove_callback_on_thread),
        "_emscripten_set_mouseup_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_mouseup_callback_on_thread),
        "_emscripten_set_touchcancel_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_touchcancel_callback_on_thread),
        "_emscripten_set_touchend_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_touchend_callback_on_thread),
        "_emscripten_set_touchmove_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_touchmove_callback_on_thread),
        "_emscripten_set_touchstart_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_touchstart_callback_on_thread),
        "_emscripten_set_wheel_callback_on_thread": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_set_wheel_callback_on_thread),
        "_emscripten_webgl_create_context": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_webgl_create_context),
        "_emscripten_webgl_destroy_context": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _emscripten_webgl_destroy_context),
        "_emscripten_webgl_enable_extension": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _emscripten_webgl_enable_extension),
        "_emscripten_webgl_get_current_context": Func(store, FuncType([], [ValType.i32()]), _emscripten_webgl_get_current_context),
        "_emscripten_webgl_init_context_attributes": Func(store, FuncType([ValType.i32()], []), _emscripten_webgl_init_context_attributes),
        "_emscripten_webgl_make_context_current": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _emscripten_webgl_make_context_current),
        "_exit": Func(store, FuncType([ValType.i32()], []), _exit),
        "_flock": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _flock),
        "_getaddrinfo": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _getaddrinfo),
        "_getenv": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _getenv),
        "_gethostbyaddr": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _gethostbyaddr),
        "_gethostbyname": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _gethostbyname),
        "_getnameinfo": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _getnameinfo),
        "_getpagesize": Func(store, FuncType([], [ValType.i32()]), _getpagesize),
        "_getpwuid": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _getpwuid),
        "_gettimeofday": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _gettimeofday),
        "_glActiveTexture": Func(store, FuncType([ValType.i32()], []), _glActiveTexture),
        "_glAttachShader": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glAttachShader),
        "_glBeginQuery": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glBeginQuery),
        "_glBeginTransformFeedback": Func(store, FuncType([ValType.i32()], []), _glBeginTransformFeedback),
        "_glBindAttribLocation": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glBindAttribLocation),
        "_glBindBuffer": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glBindBuffer),
        "_glBindBufferBase": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glBindBufferBase),
        "_glBindBufferRange": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glBindBufferRange),
        "_glBindFramebuffer": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glBindFramebuffer),
        "_glBindRenderbuffer": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glBindRenderbuffer),
        "_glBindSampler": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glBindSampler),
        "_glBindTexture": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glBindTexture),
        "_glBindTransformFeedback": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glBindTransformFeedback),
        "_glBindVertexArray": Func(store, FuncType([ValType.i32()], []), _glBindVertexArray),
        "_glBlendEquation": Func(store, FuncType([ValType.i32()], []), _glBlendEquation),
        "_glBlendEquationSeparate": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glBlendEquationSeparate),
        "_glBlendFuncSeparate": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glBlendFuncSeparate),
        "_glBlitFramebuffer": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glBlitFramebuffer),
        "_glBufferData": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glBufferData),
        "_glBufferSubData": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glBufferSubData),
        "_glCheckFramebufferStatus": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _glCheckFramebufferStatus),
        "_glClear": Func(store, FuncType([ValType.i32()], []), _glClear),
        "_glClearBufferfi": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), _glClearBufferfi),
        "_glClearBufferfv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glClearBufferfv),
        "_glClearBufferuiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glClearBufferuiv),
        "_glClearColor": Func(store, FuncType([ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64()], []), _glClearColor),
        "_glClearDepthf": Func(store, FuncType([ValType.f64()], []), _glClearDepthf),
        "_glClearStencil": Func(store, FuncType([ValType.i32()], []), _glClearStencil),
        "_glColorMask": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glColorMask),
        "_glCompileShader": Func(store, FuncType([ValType.i32()], []), _glCompileShader),
        "_glCompressedTexImage2D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glCompressedTexImage2D),
        "_glCompressedTexSubImage2D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glCompressedTexSubImage2D),
        "_glCompressedTexSubImage3D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glCompressedTexSubImage3D),
        "_glCopyBufferSubData": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glCopyBufferSubData),
        "_glCopyTexImage2D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glCopyTexImage2D),
        "_glCopyTexSubImage2D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glCopyTexSubImage2D),
        "_glCreateProgram": Func(store, FuncType([], [ValType.i32()]), _glCreateProgram),
        "_glCreateShader": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _glCreateShader),
        "_glCullFace": Func(store, FuncType([ValType.i32()], []), _glCullFace),
        "_glDeleteBuffers": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDeleteBuffers),
        "_glDeleteFramebuffers": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDeleteFramebuffers),
        "_glDeleteProgram": Func(store, FuncType([ValType.i32()], []), _glDeleteProgram),
        "_glDeleteQueries": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDeleteQueries),
        "_glDeleteRenderbuffers": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDeleteRenderbuffers),
        "_glDeleteSamplers": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDeleteSamplers),
        "_glDeleteShader": Func(store, FuncType([ValType.i32()], []), _glDeleteShader),
        "_glDeleteSync": Func(store, FuncType([ValType.i32()], []), _glDeleteSync),
        "_glDeleteTextures": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDeleteTextures),
        "_glDeleteTransformFeedbacks": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDeleteTransformFeedbacks),
        "_glDeleteVertexArrays": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDeleteVertexArrays),
        "_glDepthFunc": Func(store, FuncType([ValType.i32()], []), _glDepthFunc),
        "_glDepthMask": Func(store, FuncType([ValType.i32()], []), _glDepthMask),
        "_glDetachShader": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDetachShader),
        "_glDisable": Func(store, FuncType([ValType.i32()], []), _glDisable),
        "_glDisableVertexAttribArray": Func(store, FuncType([ValType.i32()], []), _glDisableVertexAttribArray),
        "_glDrawArrays": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glDrawArrays),
        "_glDrawArraysInstanced": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glDrawArraysInstanced),
        "_glDrawBuffers": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glDrawBuffers),
        "_glDrawElements": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glDrawElements),
        "_glDrawElementsInstanced": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glDrawElementsInstanced),
        "_glEnable": Func(store, FuncType([ValType.i32()], []), _glEnable),
        "_glEnableVertexAttribArray": Func(store, FuncType([ValType.i32()], []), _glEnableVertexAttribArray),
        "_glEndQuery": Func(store, FuncType([ValType.i32()], []), _glEndQuery),
        "_glEndTransformFeedback": Func(store, FuncType([], []), _glEndTransformFeedback),
        "_glFenceSync": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _glFenceSync),
        "_glFinish": Func(store, FuncType([], []), _glFinish),
        "_glFlush": Func(store, FuncType([], []), _glFlush),
        "_glFlushMappedBufferRange": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glFlushMappedBufferRange),
        "_glFramebufferRenderbuffer": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glFramebufferRenderbuffer),
        "_glFramebufferTexture2D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glFramebufferTexture2D),
        "_glFramebufferTextureLayer": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glFramebufferTextureLayer),
        "_glFrontFace": Func(store, FuncType([ValType.i32()], []), _glFrontFace),
        "_glGenBuffers": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glGenBuffers),
        "_glGenFramebuffers": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glGenFramebuffers),
        "_glGenQueries": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glGenQueries),
        "_glGenRenderbuffers": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glGenRenderbuffers),
        "_glGenSamplers": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glGenSamplers),
        "_glGenTextures": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glGenTextures),
        "_glGenTransformFeedbacks": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glGenTransformFeedbacks),
        "_glGenVertexArrays": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glGenVertexArrays),
        "_glGenerateMipmap": Func(store, FuncType([ValType.i32()], []), _glGenerateMipmap),
        "_glGetActiveAttrib": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetActiveAttrib),
        "_glGetActiveUniform": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetActiveUniform),
        "_glGetActiveUniformBlockName": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetActiveUniformBlockName),
        "_glGetActiveUniformBlockiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetActiveUniformBlockiv),
        "_glGetActiveUniformsiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetActiveUniformsiv),
        "_glGetAttribLocation": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _glGetAttribLocation),
        "_glGetError": Func(store, FuncType([], [ValType.i32()]), _glGetError),
        "_glGetFramebufferAttachmentParameteriv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetFramebufferAttachmentParameteriv),
        "_glGetIntegeri_v": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetIntegeri_v),
        "_glGetIntegerv": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glGetIntegerv),
        "_glGetInternalformativ": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetInternalformativ),
        "_glGetProgramBinary": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetProgramBinary),
        "_glGetProgramInfoLog": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetProgramInfoLog),
        "_glGetProgramiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetProgramiv),
        "_glGetRenderbufferParameteriv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetRenderbufferParameteriv),
        "_glGetShaderInfoLog": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetShaderInfoLog),
        "_glGetShaderPrecisionFormat": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetShaderPrecisionFormat),
        "_glGetShaderSource": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetShaderSource),
        "_glGetShaderiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetShaderiv),
        "_glGetString": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _glGetString),
        "_glGetStringi": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _glGetStringi),
        "_glGetTexParameteriv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetTexParameteriv),
        "_glGetUniformBlockIndex": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _glGetUniformBlockIndex),
        "_glGetUniformIndices": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetUniformIndices),
        "_glGetUniformLocation": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _glGetUniformLocation),
        "_glGetUniformiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetUniformiv),
        "_glGetVertexAttribiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glGetVertexAttribiv),
        "_glInvalidateFramebuffer": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glInvalidateFramebuffer),
        "_glIsEnabled": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _glIsEnabled),
        "_glIsVertexArray": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _glIsVertexArray),
        "_glLinkProgram": Func(store, FuncType([ValType.i32()], []), _glLinkProgram),
        "_glMapBufferRange": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _glMapBufferRange),
        "_glPixelStorei": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glPixelStorei),
        "_glPolygonOffset": Func(store, FuncType([ValType.f64(),ValType.f64()], []), _glPolygonOffset),
        "_glProgramBinary": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glProgramBinary),
        "_glProgramParameteri": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glProgramParameteri),
        "_glReadBuffer": Func(store, FuncType([ValType.i32()], []), _glReadBuffer),
        "_glReadPixels": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glReadPixels),
        "_glRenderbufferStorage": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glRenderbufferStorage),
        "_glRenderbufferStorageMultisample": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glRenderbufferStorageMultisample),
        "_glSamplerParameteri": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glSamplerParameteri),
        "_glScissor": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glScissor),
        "_glShaderSource": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glShaderSource),
        "_glStencilFuncSeparate": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glStencilFuncSeparate),
        "_glStencilMask": Func(store, FuncType([ValType.i32()], []), _glStencilMask),
        "_glStencilOpSeparate": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glStencilOpSeparate),
        "_glTexImage2D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glTexImage2D),
        "_glTexImage3D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glTexImage3D),
        "_glTexParameterf": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.f64()], []), _glTexParameterf),
        "_glTexParameteri": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glTexParameteri),
        "_glTexParameteriv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glTexParameteriv),
        "_glTexStorage2D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glTexStorage2D),
        "_glTexStorage3D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glTexStorage3D),
        "_glTexSubImage2D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glTexSubImage2D),
        "_glTexSubImage3D": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glTexSubImage3D),
        "_glTransformFeedbackVaryings": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glTransformFeedbackVaryings),
        "_glUniform1fv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform1fv),
        "_glUniform1i": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glUniform1i),
        "_glUniform1iv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform1iv),
        "_glUniform1uiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform1uiv),
        "_glUniform2fv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform2fv),
        "_glUniform2iv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform2iv),
        "_glUniform2uiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform2uiv),
        "_glUniform3fv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform3fv),
        "_glUniform3iv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform3iv),
        "_glUniform3uiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform3uiv),
        "_glUniform4fv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform4fv),
        "_glUniform4iv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform4iv),
        "_glUniform4uiv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniform4uiv),
        "_glUniformBlockBinding": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniformBlockBinding),
        "_glUniformMatrix3fv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniformMatrix3fv),
        "_glUniformMatrix4fv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glUniformMatrix4fv),
        "_glUnmapBuffer": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _glUnmapBuffer),
        "_glUseProgram": Func(store, FuncType([ValType.i32()], []), _glUseProgram),
        "_glValidateProgram": Func(store, FuncType([ValType.i32()], []), _glValidateProgram),
        "_glVertexAttrib4f": Func(store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64()], []), _glVertexAttrib4f),
        "_glVertexAttrib4fv": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _glVertexAttrib4fv),
        "_glVertexAttribIPointer": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glVertexAttribIPointer),
        "_glVertexAttribPointer": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glVertexAttribPointer),
        "_glViewport": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), _glViewport),
        "_gmtime": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _gmtime),
        "_inet_addr": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _inet_addr),
        "_llvm_eh_typeid_for": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _llvm_eh_typeid_for),
        "_llvm_exp2_f32": Func(store, FuncType([ValType.f64()], [ValType.f64()]), _llvm_exp2_f32),
        "_llvm_log10_f32": Func(store, FuncType([ValType.f64()], [ValType.f64()]), _llvm_log10_f32),
        "_llvm_log10_f64": Func(store, FuncType([ValType.f64()], [ValType.f64()]), _llvm_log10_f64),
        "_llvm_log2_f32": Func(store, FuncType([ValType.f64()], [ValType.f64()]), _llvm_log2_f32),
        "_llvm_trap": Func(store, FuncType([], []), _llvm_trap),
        "_llvm_trunc_f32": Func(store, FuncType([ValType.f64()], [ValType.f64()]), _llvm_trunc_f32),
        "_localtime": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _localtime),
        "_longjmp": Func(store, FuncType([ValType.i32(),ValType.i32()], []), _longjmp),
        "_mktime": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _mktime),
        "_pthread_cond_destroy": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _pthread_cond_destroy),
        "_pthread_cond_init": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _pthread_cond_init),
        "_pthread_cond_timedwait": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _pthread_cond_timedwait),
        "_pthread_cond_wait": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _pthread_cond_wait),
        "_pthread_getspecific": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _pthread_getspecific),
        "_pthread_key_create": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _pthread_key_create),
        "_pthread_key_delete": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _pthread_key_delete),
        "_pthread_mutex_destroy": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _pthread_mutex_destroy),
        "_pthread_mutex_init": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _pthread_mutex_init),
        "_pthread_mutexattr_destroy": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _pthread_mutexattr_destroy),
        "_pthread_mutexattr_init": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _pthread_mutexattr_init),
        "_pthread_mutexattr_setprotocol": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _pthread_mutexattr_setprotocol),
        "_pthread_mutexattr_settype": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _pthread_mutexattr_settype),
        "_pthread_once": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _pthread_once),
        "_pthread_setspecific": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _pthread_setspecific),
        "_sched_yield": Func(store, FuncType([], [ValType.i32()]), _sched_yield),
        "_setenv": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _setenv),
        "_sigaction": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _sigaction),
        "_sigemptyset": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _sigemptyset),
        "_strftime": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _strftime),
        "_sysconf": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _sysconf),
        "_time": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _time),
        "_unsetenv": Func(store, FuncType([ValType.i32()], [ValType.i32()]), _unsetenv),
        "_utime": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), _utime),
        "f64_rem": Func(store, FuncType([ValType.f64(),ValType.f64()], [ValType.f64()]), f64_rem),
        "invoke_iiiiij": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiiij),
        "invoke_iiiijii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiijii),
        "invoke_iiiijjii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiijjii),
        "invoke_iiiji": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiiji),
        "invoke_iiijiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiijiii),
        "invoke_iij": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iij),
        "invoke_iiji": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iiji),
        "invoke_iijii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_iijii),
        "invoke_ijii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_ijii),
        "invoke_j": Func(store, FuncType([ValType.i32()], [ValType.i32()]), invoke_j),
        "invoke_jdi": Func(store, FuncType([ValType.i32(),ValType.f64(),ValType.i32()], [ValType.i32()]), invoke_jdi),
        "invoke_ji": Func(store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_ji),
        "invoke_jii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jii),
        "invoke_jiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jiii),
        "invoke_jiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jiiii),
        "invoke_jiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jiiiii),
        "invoke_jiiiiiiiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jiiiiiiiiii),
        "invoke_jiiij": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jiiij),
        "invoke_jiiji": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jiiji),
        "invoke_jiji": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jiji),
        "invoke_jijii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jijii),
        "invoke_jijiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jijiii),
        "invoke_jijj": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jijj),
        "invoke_jji": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), invoke_jji),
        "invoke_viiiiiiifjjfii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), invoke_viiiiiiifjjfii),
        "invoke_viiiijiiii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiiijiiii),
        "invoke_viiij": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiij),
        "invoke_viiiji": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiiji),
        "invoke_viij": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viij),
        "invoke_viiji": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viiji),
        "invoke_viijji": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viijji),
        "invoke_viji": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_viji),
        "invoke_vijii": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), invoke_vijii),
        "___atomic_fetch_add_8": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), ___atomic_fetch_add_8),
        "_glClientWaitSync": Func(store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), _glClientWaitSync),
}}

test = [memory, 
 table, 
 global_tableBase,
 global_DYNAMICTOP_PTR,
 global_STACKTOP,
 global_STACK_MAX,
 Global(store, global_type64, Val.f64(float('nan'))),
 Global(store, global_type64, Val.f64(float('inf'))),
 Func(store, FuncType([ValType.f64(), ValType.f64()], [ValType.f64()]), pow),
]+list(import_object['env'].values())

instance = Instance(store, wasm_module, test)
from functools import partial
__growWasmMemory = partial(instance.exports(store)["__growWasmMemory"], store)
stackAlloc = partial(instance.exports(store)["stackAlloc"], store)
stackSave = partial(instance.exports(store)["stackSave"], store)
stackRestore = partial(instance.exports(store)["stackRestore"], store)
establishStackSpace = partial(instance.exports(store)["establishStackSpace"], store)
setThrew = partial(instance.exports(store)["setThrew"], store)
setTempRet0 = partial(instance.exports(store)["setTempRet0"], store)
getTempRet0 = partial(instance.exports(store)["getTempRet0"], store)
__GLOBAL__sub_I_AIScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_AIScriptingClasses_cpp"], store)
___cxx_global_var_init = partial(instance.exports(store)["___cxx_global_var_init"], store)
_pthread_mutex_unlock = partial(instance.exports(store)["_pthread_mutex_unlock"], store)
runPostSets = partial(instance.exports(store)["runPostSets"], store)
__GLOBAL__sub_I_AccessibilityScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_AccessibilityScriptingClasses_cpp"], store)
__GLOBAL__sub_I_AndroidJNIScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_AndroidJNIScriptingClasses_cpp"], store)
__GLOBAL__sub_I_AnimationScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_AnimationScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Animation_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Animation_1_cpp"], store)
__GLOBAL__sub_I_Modules_Animation_3_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Animation_3_cpp"], store)
__GLOBAL__sub_I_Modules_Animation_6_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Animation_6_cpp"], store)
__GLOBAL__sub_I_Avatar_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Avatar_cpp"], store)
__GLOBAL__sub_I_ConstraintManager_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_ConstraintManager_cpp"], store)
__GLOBAL__sub_I_AnimationClip_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_AnimationClip_cpp"], store)
__GLOBAL__sub_I_AssetBundleScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_AssetBundleScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_AssetBundle_Public_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_AssetBundle_Public_0_cpp"], store)
__GLOBAL__sub_I_AudioScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_AudioScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Runtime_Video_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Video_0_cpp"], store)
__GLOBAL__sub_I_Modules_Audio_Public_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Audio_Public_0_cpp"], store)
__GLOBAL__sub_I_Modules_Audio_Public_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Audio_Public_1_cpp"], store)
__GLOBAL__sub_I_Modules_Audio_Public_3_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Audio_Public_3_cpp"], store)
__GLOBAL__sub_I_Modules_Audio_Public_ScriptBindings_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Audio_Public_ScriptBindings_1_cpp"], store)
__GLOBAL__sub_I_Modules_Audio_Public_sound_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Audio_Public_sound_0_cpp"], store)
__GLOBAL__sub_I_ClothScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_ClothScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Cloth_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Cloth_0_cpp"], store)
___cxx_global_var_init_18 = partial(instance.exports(store)["___cxx_global_var_init_18"], store)
__GLOBAL__sub_I_nvcloth_src_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_nvcloth_src_0_cpp"], store)
__GLOBAL__sub_I_nvcloth_src_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_nvcloth_src_1_cpp"], store)
__GLOBAL__sub_I_SwInterCollision_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_SwInterCollision_cpp"], store)
__GLOBAL__sub_I_SwSolverKernel_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_SwSolverKernel_cpp"], store)
__GLOBAL__sub_I_artifacts_WebGL_codegenerator_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_artifacts_WebGL_codegenerator_0_cpp"], store)
__GLOBAL__sub_I_Runtime_GfxDevice_opengles_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_GfxDevice_opengles_0_cpp"], store)
__GLOBAL__sub_I_Runtime_VirtualFileSystem_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_VirtualFileSystem_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Input_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Input_0_cpp"], store)
__GLOBAL__sub_I_GfxDeviceNull_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_GfxDeviceNull_cpp"], store)
__GLOBAL__sub_I_External_ProphecySDK_BlitOperations_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_External_ProphecySDK_BlitOperations_1_cpp"], store)
__GLOBAL__sub_I_Runtime_2D_Renderer_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_2D_Renderer_0_cpp"], store)
__GLOBAL__sub_I_Runtime_2D_Sorting_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_2D_Sorting_0_cpp"], store)
__GLOBAL__sub_I_Runtime_2D_SpriteAtlas_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_2D_SpriteAtlas_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Allocator_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Allocator_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Allocator_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Allocator_2_cpp"], store)
___cxx_global_var_init_7 = partial(instance.exports(store)["___cxx_global_var_init_7"], store)
__GLOBAL__sub_I_Runtime_Application_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Application_0_cpp"], store)
__GLOBAL__sub_I_Runtime_BaseClasses_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_BaseClasses_0_cpp"], store)
__GLOBAL__sub_I_Runtime_BaseClasses_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_BaseClasses_1_cpp"], store)
__GLOBAL__sub_I_Runtime_BaseClasses_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_BaseClasses_2_cpp"], store)
__GLOBAL__sub_I_Runtime_BaseClasses_3_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_BaseClasses_3_cpp"], store)
__GLOBAL__sub_I_Runtime_Burst_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Burst_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_3_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_3_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_4_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_4_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_5_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_5_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_6_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_6_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_7_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_7_cpp"], store)
__GLOBAL__sub_I_Shadows_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Shadows_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_Culling_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_Culling_0_cpp"], store)
__GLOBAL__sub_I_GUITexture_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_GUITexture_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_RenderLoops_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_RenderLoops_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Camera_RenderLoops_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Camera_RenderLoops_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Containers_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Containers_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Core_Callbacks_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Core_Callbacks_0_cpp"], store)
__GLOBAL__sub_I_Runtime_File_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_File_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Geometry_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Geometry_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_0_cpp"], store)
___cxx_global_var_init_98 = partial(instance.exports(store)["___cxx_global_var_init_98"], store)
__GLOBAL__sub_I_Runtime_Graphics_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_4_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_4_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_5_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_5_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_6_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_6_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_8_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_8_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_10_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_10_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_11_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_11_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_Billboard_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_Billboard_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_LOD_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_LOD_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_Mesh_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_Mesh_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_Mesh_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_Mesh_4_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_4_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_Mesh_5_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_5_cpp"], store)
__GLOBAL__sub_I_Runtime_Graphics_ScriptableRenderLoop_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Graphics_ScriptableRenderLoop_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Interfaces_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Interfaces_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Interfaces_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Interfaces_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Interfaces_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Interfaces_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Jobs_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Jobs_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Jobs_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Jobs_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Jobs_Internal_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Jobs_Internal_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Jobs_ScriptBindings_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Jobs_ScriptBindings_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Math_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Math_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Math_Random_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Math_Random_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Misc_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Misc_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Misc_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Misc_2_cpp"], store)
___cxx_global_var_init_131 = partial(instance.exports(store)["___cxx_global_var_init_131"], store)
__GLOBAL__sub_I_Runtime_Misc_4_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Misc_4_cpp"], store)
__GLOBAL__sub_I_Runtime_Misc_5_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Misc_5_cpp"], store)
__GLOBAL__sub_I_Runtime_PreloadManager_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_PreloadManager_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Profiler_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Profiler_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Profiler_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Profiler_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Profiler_ScriptBindings_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Profiler_ScriptBindings_0_cpp"], store)
__GLOBAL__sub_I_Runtime_SceneManager_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_SceneManager_0_cpp"], store)
___cxx_global_var_init_8100 = partial(instance.exports(store)["___cxx_global_var_init_8100"], store)
__GLOBAL__sub_I_Runtime_Shaders_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Shaders_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Shaders_3_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Shaders_3_cpp"], store)
__GLOBAL__sub_I_Runtime_Shaders_4_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Shaders_4_cpp"], store)
__GLOBAL__sub_I_Runtime_Shaders_ShaderImpl_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Shaders_ShaderImpl_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Transform_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Transform_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Transform_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Transform_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Utilities_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Utilities_2_cpp"], store)
___cxx_global_var_init_2_9504 = partial(instance.exports(store)["___cxx_global_var_init_2_9504"], store)
__GLOBAL__sub_I_Runtime_Utilities_5_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Utilities_5_cpp"], store)
__GLOBAL__sub_I_Runtime_Utilities_6_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Utilities_6_cpp"], store)
__GLOBAL__sub_I_Runtime_Utilities_7_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Utilities_7_cpp"], store)
__GLOBAL__sub_I_Runtime_Utilities_9_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Utilities_9_cpp"], store)
__GLOBAL__sub_I_AssetBundleFileSystem_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_AssetBundleFileSystem_cpp"], store)
__GLOBAL__sub_I_Runtime_Modules_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Modules_0_cpp"], store)
___cxx_global_var_init_13 = partial(instance.exports(store)["___cxx_global_var_init_13"], store)
___cxx_global_var_init_14 = partial(instance.exports(store)["___cxx_global_var_init_14"], store)
___cxx_global_var_init_15 = partial(instance.exports(store)["___cxx_global_var_init_15"], store)
__GLOBAL__sub_I_Modules_Profiler_Public_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Profiler_Public_0_cpp"], store)
__GLOBAL__sub_I_Modules_Profiler_Runtime_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Profiler_Runtime_1_cpp"], store)
__GLOBAL__sub_I_UnsafeUtility_bindings_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_UnsafeUtility_bindings_cpp"], store)
__GLOBAL__sub_I_Runtime_GfxDevice_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_GfxDevice_1_cpp"], store)
__GLOBAL__sub_I_Runtime_GfxDevice_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_GfxDevice_2_cpp"], store)
__GLOBAL__sub_I_Runtime_GfxDevice_3_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_GfxDevice_3_cpp"], store)
__GLOBAL__sub_I_Runtime_GfxDevice_4_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_GfxDevice_4_cpp"], store)
__GLOBAL__sub_I_Runtime_GfxDevice_5_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_GfxDevice_5_cpp"], store)
__GLOBAL__sub_I_Runtime_PluginInterface_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_PluginInterface_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Director_Core_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Director_Core_1_cpp"], store)
__GLOBAL__sub_I_Runtime_ScriptingBackend_Il2Cpp_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_ScriptingBackend_Il2Cpp_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Scripting_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Scripting_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Scripting_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Scripting_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Scripting_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Scripting_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Scripting_3_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Scripting_3_cpp"], store)
__GLOBAL__sub_I_Runtime_Mono_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Mono_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_1_cpp"], store)
__GLOBAL__sub_I_TemplateInstantiations_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_TemplateInstantiations_cpp"], store)
__GLOBAL__sub_I_Runtime_Scripting_APIUpdating_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Scripting_APIUpdating_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Serialize_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Serialize_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Serialize_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Serialize_1_cpp"], store)
__GLOBAL__sub_I_Runtime_Serialize_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Serialize_2_cpp"], store)
__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_0_cpp"], store)
__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_1_cpp"], store)
__GLOBAL__sub_I_PlatformDependent_WebGL_Source_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_PlatformDependent_WebGL_Source_0_cpp"], store)
__GLOBAL__sub_I_PlatformDependent_WebGL_Source_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_PlatformDependent_WebGL_Source_2_cpp"], store)
__GLOBAL__sub_I_LogAssert_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_LogAssert_cpp"], store)
__GLOBAL__sub_I_Shader_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Shader_cpp"], store)
__GLOBAL__sub_I_Transform_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Transform_cpp"], store)
__GLOBAL__sub_I_PlatformDependent_WebGL_External_baselib_builds_Source_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_PlatformDependent_WebGL_External_baselib_builds_Source_0_cpp"], store)
_SendMessage = partial(instance.exports(store)["_SendMessage"], store)
_SendMessageString = partial(instance.exports(store)["_SendMessageString"], store)
_SetFullscreen = partial(instance.exports(store)["_SetFullscreen"], store)
_main = partial(instance.exports(store)["_main"], store)
__GLOBAL__sub_I_Modules_DSPGraph_Public_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_DSPGraph_Public_1_cpp"], store)
__GLOBAL__sub_I_DirectorScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_DirectorScriptingClasses_cpp"], store)
__GLOBAL__sub_I_GridScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_GridScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Grid_Public_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Grid_Public_0_cpp"], store)
__GLOBAL__sub_I_IMGUIScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_IMGUIScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_IMGUI_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_IMGUI_0_cpp"], store)
___cxx_global_var_init_22 = partial(instance.exports(store)["___cxx_global_var_init_22"], store)
__GLOBAL__sub_I_Modules_IMGUI_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_IMGUI_1_cpp"], store)
___cxx_global_var_init_3893 = partial(instance.exports(store)["___cxx_global_var_init_3893"], store)
__GLOBAL__sub_I_InputLegacyScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_InputLegacyScriptingClasses_cpp"], store)
__GLOBAL__sub_I_InputScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_InputScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Input_Private_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Input_Private_0_cpp"], store)
__GLOBAL__sub_I_ParticleSystemScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_ParticleSystemScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_ParticleSystem_Modules_3_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_ParticleSystem_Modules_3_cpp"], store)
__GLOBAL__sub_I_ParticleSystemRenderer_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_ParticleSystemRenderer_cpp"], store)
__GLOBAL__sub_I_ShapeModule_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_ShapeModule_cpp"], store)
__GLOBAL__sub_I_Physics2DScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Physics2DScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Physics2D_Public_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Physics2D_Public_0_cpp"], store)
__GLOBAL__sub_I_Modules_Physics2D_Public_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Physics2D_Public_1_cpp"], store)
__GLOBAL__sub_I_PhysicsScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_PhysicsScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Physics_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Physics_0_cpp"], store)
__GLOBAL__sub_I_Modules_Physics_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Physics_1_cpp"], store)
__GLOBAL__sub_I_PhysicsQuery_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_PhysicsQuery_cpp"], store)
__GLOBAL__sub_I_SubsystemsScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_SubsystemsScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Subsystems_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Subsystems_0_cpp"], store)
__GLOBAL__sub_I_TerrainScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_TerrainScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Terrain_Public_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Terrain_Public_0_cpp"], store)
___cxx_global_var_init_69 = partial(instance.exports(store)["___cxx_global_var_init_69"], store)
__GLOBAL__sub_I_Modules_Terrain_Public_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Terrain_Public_1_cpp"], store)
__GLOBAL__sub_I_Modules_Terrain_Public_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Terrain_Public_2_cpp"], store)
__GLOBAL__sub_I_Modules_Terrain_Public_3_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Terrain_Public_3_cpp"], store)
__GLOBAL__sub_I_Modules_Terrain_VR_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Terrain_VR_0_cpp"], store)
__GLOBAL__sub_I_TextCoreScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_TextCoreScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_TextCore_Native_FontEngine_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_TextCore_Native_FontEngine_0_cpp"], store)
__GLOBAL__sub_I_TextRenderingScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_TextRenderingScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_TextRendering_Public_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_TextRendering_Public_0_cpp"], store)
__GLOBAL__sub_I_TilemapScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_TilemapScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Tilemap_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Tilemap_0_cpp"], store)
__GLOBAL__sub_I_Modules_Tilemap_Public_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Tilemap_Public_0_cpp"], store)
__GLOBAL__sub_I_UIElementsScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_UIElementsScriptingClasses_cpp"], store)
__GLOBAL__sub_I_External_Yoga_Yoga_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_External_Yoga_Yoga_0_cpp"], store)
__GLOBAL__sub_I_UIScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_UIScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_UI_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_UI_0_cpp"], store)
__GLOBAL__sub_I_Modules_UI_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_UI_1_cpp"], store)
__GLOBAL__sub_I_Modules_UI_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_UI_2_cpp"], store)
__GLOBAL__sub_I_umbra_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_umbra_cpp"], store)
__GLOBAL__sub_I_UnityAnalyticsScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_UnityAnalyticsScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_UnityAnalytics_Dispatcher_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_UnityAnalytics_Dispatcher_0_cpp"], store)
__GLOBAL__sub_I_UnityAdsSettings_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_UnityAdsSettings_cpp"], store)
__GLOBAL__sub_I_UnityWebRequestScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_UnityWebRequestScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_UnityWebRequest_Public_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_UnityWebRequest_Public_0_cpp"], store)
__GLOBAL__sub_I_VFXScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_VFXScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_VFX_Public_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_VFX_Public_1_cpp"], store)
__GLOBAL__sub_I_Modules_VFX_Public_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_VFX_Public_2_cpp"], store)
__GLOBAL__sub_I_VRScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_VRScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_VR_2_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_VR_2_cpp"], store)
__GLOBAL__sub_I_Modules_VR_PluginInterface_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_VR_PluginInterface_0_cpp"], store)
__GLOBAL__sub_I_VideoScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_VideoScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_Video_Public_Base_0_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_Video_Public_Base_0_cpp"], store)
__GLOBAL__sub_I_Wind_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Wind_cpp"], store)
__GLOBAL__sub_I_XRScriptingClasses_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_XRScriptingClasses_cpp"], store)
__GLOBAL__sub_I_Modules_XR_Subsystems_Input_Public_1_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Modules_XR_Subsystems_Input_Public_1_cpp"], store)
__GLOBAL__sub_I_Lump_libil2cpp_os_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Lump_libil2cpp_os_cpp"], store)
__GLOBAL__sub_I_Il2CppCodeRegistration_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Il2CppCodeRegistration_cpp"], store)
__GLOBAL__sub_I_Lump_libil2cpp_vm_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Lump_libil2cpp_vm_cpp"], store)
__GLOBAL__sub_I_Lump_libil2cpp_metadata_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Lump_libil2cpp_metadata_cpp"], store)
__GLOBAL__sub_I_Lump_libil2cpp_utils_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Lump_libil2cpp_utils_cpp"], store)
__GLOBAL__sub_I_Lump_libil2cpp_gc_cpp = partial(instance.exports(store)["__GLOBAL__sub_I_Lump_libil2cpp_gc_cpp"], store)
_malloc = partial(instance.exports(store)["_malloc"], store)
_free = partial(instance.exports(store)["_free"], store)
_realloc = partial(instance.exports(store)["_realloc"], store)
_memalign = partial(instance.exports(store)["_memalign"], store)
___errno_location = partial(instance.exports(store)["___errno_location"], store)
_strlen = partial(instance.exports(store)["_strlen"], store)
_ntohs = partial(instance.exports(store)["_ntohs"], store)
_htonl = partial(instance.exports(store)["_htonl"], store)
___emscripten_environ_constructor = partial(instance.exports(store)["___emscripten_environ_constructor"], store)
__get_tzname = partial(instance.exports(store)["__get_tzname"], store)
__get_daylight = partial(instance.exports(store)["__get_daylight"], store)
__get_timezone = partial(instance.exports(store)["__get_timezone"], store)
__get_environ = partial(instance.exports(store)["__get_environ"], store)
___cxa_can_catch = partial(instance.exports(store)["___cxa_can_catch"], store)
___cxa_is_pointer_type = partial(instance.exports(store)["___cxa_is_pointer_type"], store)
_i64Add = partial(instance.exports(store)["_i64Add"], store)
_saveSetjmp = partial(instance.exports(store)["_saveSetjmp"], store)
_testSetjmp = partial(instance.exports(store)["_testSetjmp"], store)
_llvm_bswap_i32 = partial(instance.exports(store)["_llvm_bswap_i32"], store)
_llvm_ctlz_i64 = partial(instance.exports(store)["_llvm_ctlz_i64"], store)
_llvm_ctpop_i32 = partial(instance.exports(store)["_llvm_ctpop_i32"], store)
_llvm_maxnum_f64 = partial(instance.exports(store)["_llvm_maxnum_f64"], store)
_llvm_minnum_f32 = partial(instance.exports(store)["_llvm_minnum_f32"], store)
_llvm_round_f32 = partial(instance.exports(store)["_llvm_round_f32"], store)
_memcpy = partial(instance.exports(store)["_memcpy"], store)
_memmove = partial(instance.exports(store)["_memmove"], store)
_memset = partial(instance.exports(store)["_memset"], store)
_rintf = partial(instance.exports(store)["_rintf"], store)
_sbrk = partial(instance.exports(store)["_sbrk"], store)
dynCall_dddi = partial(instance.exports(store)["dynCall_dddi"], store)
dynCall_ddi = partial(instance.exports(store)["dynCall_ddi"], store)
dynCall_ddidi = partial(instance.exports(store)["dynCall_ddidi"], store)
dynCall_ddii = partial(instance.exports(store)["dynCall_ddii"], store)
dynCall_ddiii = partial(instance.exports(store)["dynCall_ddiii"], store)
dynCall_di = partial(instance.exports(store)["dynCall_di"], store)
dynCall_diddi = partial(instance.exports(store)["dynCall_diddi"], store)
dynCall_didi = partial(instance.exports(store)["dynCall_didi"], store)
dynCall_dii = partial(instance.exports(store)["dynCall_dii"], store)
dynCall_diidi = partial(instance.exports(store)["dynCall_diidi"], store)
dynCall_diii = partial(instance.exports(store)["dynCall_diii"], store)
dynCall_diiid = partial(instance.exports(store)["dynCall_diiid"], store)
dynCall_diiii = partial(instance.exports(store)["dynCall_diiii"], store)
dynCall_diiiii = partial(instance.exports(store)["dynCall_diiiii"], store)
dynCall_i = partial(instance.exports(store)["dynCall_i"], store)
dynCall_idddi = partial(instance.exports(store)["dynCall_idddi"], store)
dynCall_iddi = partial(instance.exports(store)["dynCall_iddi"], store)
dynCall_iddii = partial(instance.exports(store)["dynCall_iddii"], store)
dynCall_idi = partial(instance.exports(store)["dynCall_idi"], store)
dynCall_idii = partial(instance.exports(store)["dynCall_idii"], store)
dynCall_idiii = partial(instance.exports(store)["dynCall_idiii"], store)
dynCall_idiiii = partial(instance.exports(store)["dynCall_idiiii"], store)
dynCall_ii = partial(instance.exports(store)["dynCall_ii"], store)
dynCall_iiddi = partial(instance.exports(store)["dynCall_iiddi"], store)
dynCall_iidi = partial(instance.exports(store)["dynCall_iidi"], store)
dynCall_iidii = partial(instance.exports(store)["dynCall_iidii"], store)
dynCall_iidiii = partial(instance.exports(store)["dynCall_iidiii"], store)
dynCall_iii = partial(instance.exports(store)["dynCall_iii"], store)
dynCall_iiiddi = partial(instance.exports(store)["dynCall_iiiddi"], store)
dynCall_iiidi = partial(instance.exports(store)["dynCall_iiidi"], store)
dynCall_iiidii = partial(instance.exports(store)["dynCall_iiidii"], store)
dynCall_iiidiii = partial(instance.exports(store)["dynCall_iiidiii"], store)
dynCall_iiii = partial(instance.exports(store)["dynCall_iiii"], store)
dynCall_iiiii = partial(instance.exports(store)["dynCall_iiiii"], store)
dynCall_iiiiidii = partial(instance.exports(store)["dynCall_iiiiidii"], store)
dynCall_iiiiii = partial(instance.exports(store)["dynCall_iiiiii"], store)
dynCall_iiiiiii = partial(instance.exports(store)["dynCall_iiiiiii"], store)
dynCall_iiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiii"], store)
dynCall_iiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiii"], store)
dynCall_iiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiii"], store)
dynCall_iiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiii"], store)
dynCall_iiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiii"], store)
dynCall_iiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiiii"], store)
dynCall_iiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiiiii"], store)
dynCall_iiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiiiiii"], store)
dynCall_iiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiiiiiii"], store)
dynCall_iiiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiiiiiiii"], store)
dynCall_iiiiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiiiiiiiii"], store)
dynCall_iiiiiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiiiiiiiiii"], store)
dynCall_iiiiiiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiiiiiiiiiii"], store)
dynCall_iiiiiiiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiiiiiiiiiiiiiiii"], store)
dynCall_v = partial(instance.exports(store)["dynCall_v"], store)
dynCall_vd = partial(instance.exports(store)["dynCall_vd"], store)
dynCall_vdi = partial(instance.exports(store)["dynCall_vdi"], store)
dynCall_vi = partial(instance.exports(store)["dynCall_vi"], store)
dynCall_vid = partial(instance.exports(store)["dynCall_vid"], store)
dynCall_vidd = partial(instance.exports(store)["dynCall_vidd"], store)
dynCall_vidddi = partial(instance.exports(store)["dynCall_vidddi"], store)
dynCall_viddi = partial(instance.exports(store)["dynCall_viddi"], store)
dynCall_viddiiii = partial(instance.exports(store)["dynCall_viddiiii"], store)
dynCall_vidi = partial(instance.exports(store)["dynCall_vidi"], store)
dynCall_vidii = partial(instance.exports(store)["dynCall_vidii"], store)
dynCall_vidiii = partial(instance.exports(store)["dynCall_vidiii"], store)
dynCall_vii = partial(instance.exports(store)["dynCall_vii"], store)
dynCall_viid = partial(instance.exports(store)["dynCall_viid"], store)
dynCall_viidd = partial(instance.exports(store)["dynCall_viidd"], store)
dynCall_viidi = partial(instance.exports(store)["dynCall_viidi"], store)
dynCall_viidii = partial(instance.exports(store)["dynCall_viidii"], store)
dynCall_viii = partial(instance.exports(store)["dynCall_viii"], store)
dynCall_viiidi = partial(instance.exports(store)["dynCall_viiidi"], store)
dynCall_viiii = partial(instance.exports(store)["dynCall_viiii"], store)
dynCall_viiiiddi = partial(instance.exports(store)["dynCall_viiiiddi"], store)
dynCall_viiiii = partial(instance.exports(store)["dynCall_viiiii"], store)
dynCall_viiiiii = partial(instance.exports(store)["dynCall_viiiiii"], store)
dynCall_viiiiiii = partial(instance.exports(store)["dynCall_viiiiiii"], store)
dynCall_viiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiii"], store)
dynCall_viiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiii"], store)
dynCall_viiiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiiii"], store)
dynCall_viiiiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiiiii"], store)
dynCall_viiiiiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiiiiii"], store)
dynCall_viiiiiiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiiiiiii"], store)
dynCall_viiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiiiiiiii"], store)
dynCall_viiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiiiiiiiii"], store)
dynCall_viiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiiiiiiiiii"], store)
dynCall_viiiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiiiiiiiiiii"], store)
dynCall_viiiiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_viiiiiiiiiiiiiiiiii"], store)
_SendMessageFloat = partial(instance.exports(store)["_SendMessageFloat"], store)
dynCall_dfi = partial(instance.exports(store)["dynCall_dfi"], store)
dynCall_dij = partial(instance.exports(store)["dynCall_dij"], store)
dynCall_diji = partial(instance.exports(store)["dynCall_diji"], store)
dynCall_dji = partial(instance.exports(store)["dynCall_dji"], store)
dynCall_f = partial(instance.exports(store)["dynCall_f"], store)
dynCall_fdi = partial(instance.exports(store)["dynCall_fdi"], store)
dynCall_ff = partial(instance.exports(store)["dynCall_ff"], store)
dynCall_fff = partial(instance.exports(store)["dynCall_fff"], store)
dynCall_ffff = partial(instance.exports(store)["dynCall_ffff"], store)
dynCall_fffff = partial(instance.exports(store)["dynCall_fffff"], store)
dynCall_ffffffi = partial(instance.exports(store)["dynCall_ffffffi"], store)
dynCall_fffffi = partial(instance.exports(store)["dynCall_fffffi"], store)
dynCall_ffffi = partial(instance.exports(store)["dynCall_ffffi"], store)
dynCall_ffffii = partial(instance.exports(store)["dynCall_ffffii"], store)
dynCall_fffi = partial(instance.exports(store)["dynCall_fffi"], store)
dynCall_fffiffffffi = partial(instance.exports(store)["dynCall_fffiffffffi"], store)
dynCall_fffifffffi = partial(instance.exports(store)["dynCall_fffifffffi"], store)
dynCall_fffifffi = partial(instance.exports(store)["dynCall_fffifffi"], store)
dynCall_fffifi = partial(instance.exports(store)["dynCall_fffifi"], store)
dynCall_fffii = partial(instance.exports(store)["dynCall_fffii"], store)
dynCall_fffiii = partial(instance.exports(store)["dynCall_fffiii"], store)
dynCall_ffi = partial(instance.exports(store)["dynCall_ffi"], store)
dynCall_fi = partial(instance.exports(store)["dynCall_fi"], store)
dynCall_fidi = partial(instance.exports(store)["dynCall_fidi"], store)
dynCall_fif = partial(instance.exports(store)["dynCall_fif"], store)
dynCall_fiff = partial(instance.exports(store)["dynCall_fiff"], store)
dynCall_fiffffi = partial(instance.exports(store)["dynCall_fiffffi"], store)
dynCall_fifffi = partial(instance.exports(store)["dynCall_fifffi"], store)
dynCall_fiffi = partial(instance.exports(store)["dynCall_fiffi"], store)
dynCall_fifi = partial(instance.exports(store)["dynCall_fifi"], store)
dynCall_fifii = partial(instance.exports(store)["dynCall_fifii"], store)
dynCall_fii = partial(instance.exports(store)["dynCall_fii"], store)
dynCall_fiif = partial(instance.exports(store)["dynCall_fiif"], store)
dynCall_fiifdi = partial(instance.exports(store)["dynCall_fiifdi"], store)
dynCall_fiiffffi = partial(instance.exports(store)["dynCall_fiiffffi"], store)
dynCall_fiiffi = partial(instance.exports(store)["dynCall_fiiffi"], store)
dynCall_fiifi = partial(instance.exports(store)["dynCall_fiifi"], store)
dynCall_fiifii = partial(instance.exports(store)["dynCall_fiifii"], store)
dynCall_fiifji = partial(instance.exports(store)["dynCall_fiifji"], store)
dynCall_fiii = partial(instance.exports(store)["dynCall_fiii"], store)
dynCall_fiiif = partial(instance.exports(store)["dynCall_fiiif"], store)
dynCall_fiiii = partial(instance.exports(store)["dynCall_fiiii"], store)
dynCall_fiiiif = partial(instance.exports(store)["dynCall_fiiiif"], store)
dynCall_fiiiii = partial(instance.exports(store)["dynCall_fiiiii"], store)
dynCall_fiiiiii = partial(instance.exports(store)["dynCall_fiiiiii"], store)
dynCall_fiiiiiifiifif = partial(instance.exports(store)["dynCall_fiiiiiifiifif"], store)
dynCall_fiiiiiifiiiif = partial(instance.exports(store)["dynCall_fiiiiiifiiiif"], store)
dynCall_fji = partial(instance.exports(store)["dynCall_fji"], store)
dynCall_iffffffi = partial(instance.exports(store)["dynCall_iffffffi"], store)
dynCall_iffffi = partial(instance.exports(store)["dynCall_iffffi"], store)
dynCall_ifffi = partial(instance.exports(store)["dynCall_ifffi"], store)
dynCall_iffi = partial(instance.exports(store)["dynCall_iffi"], store)
dynCall_ifi = partial(instance.exports(store)["dynCall_ifi"], store)
dynCall_ifii = partial(instance.exports(store)["dynCall_ifii"], store)
dynCall_ifiii = partial(instance.exports(store)["dynCall_ifiii"], store)
dynCall_ifiiii = partial(instance.exports(store)["dynCall_ifiiii"], store)
dynCall_iif = partial(instance.exports(store)["dynCall_iif"], store)
dynCall_iiff = partial(instance.exports(store)["dynCall_iiff"], store)
dynCall_iifff = partial(instance.exports(store)["dynCall_iifff"], store)
dynCall_iiffffffiii = partial(instance.exports(store)["dynCall_iiffffffiii"], store)
dynCall_iiffffi = partial(instance.exports(store)["dynCall_iiffffi"], store)
dynCall_iiffffiii = partial(instance.exports(store)["dynCall_iiffffiii"], store)
dynCall_iifffi = partial(instance.exports(store)["dynCall_iifffi"], store)
dynCall_iifffiii = partial(instance.exports(store)["dynCall_iifffiii"], store)
dynCall_iiffi = partial(instance.exports(store)["dynCall_iiffi"], store)
dynCall_iiffifiii = partial(instance.exports(store)["dynCall_iiffifiii"], store)
dynCall_iiffii = partial(instance.exports(store)["dynCall_iiffii"], store)
dynCall_iiffiii = partial(instance.exports(store)["dynCall_iiffiii"], store)
dynCall_iiffiiiii = partial(instance.exports(store)["dynCall_iiffiiiii"], store)
dynCall_iifi = partial(instance.exports(store)["dynCall_iifi"], store)
dynCall_iifii = partial(instance.exports(store)["dynCall_iifii"], store)
dynCall_iifiifii = partial(instance.exports(store)["dynCall_iifiifii"], store)
dynCall_iifiifiii = partial(instance.exports(store)["dynCall_iifiifiii"], store)
dynCall_iifiii = partial(instance.exports(store)["dynCall_iifiii"], store)
dynCall_iifiiii = partial(instance.exports(store)["dynCall_iifiiii"], store)
dynCall_iifiiiii = partial(instance.exports(store)["dynCall_iifiiiii"], store)
dynCall_iifiiiiii = partial(instance.exports(store)["dynCall_iifiiiiii"], store)
dynCall_iiif = partial(instance.exports(store)["dynCall_iiif"], store)
dynCall_iiiffffi = partial(instance.exports(store)["dynCall_iiiffffi"], store)
dynCall_iiifffi = partial(instance.exports(store)["dynCall_iiifffi"], store)
dynCall_iiifffii = partial(instance.exports(store)["dynCall_iiifffii"], store)
dynCall_iiiffi = partial(instance.exports(store)["dynCall_iiiffi"], store)
dynCall_iiiffifiii = partial(instance.exports(store)["dynCall_iiiffifiii"], store)
dynCall_iiiffii = partial(instance.exports(store)["dynCall_iiiffii"], store)
dynCall_iiiffiii = partial(instance.exports(store)["dynCall_iiiffiii"], store)
dynCall_iiifi = partial(instance.exports(store)["dynCall_iiifi"], store)
dynCall_iiififi = partial(instance.exports(store)["dynCall_iiififi"], store)
dynCall_iiififii = partial(instance.exports(store)["dynCall_iiififii"], store)
dynCall_iiififiii = partial(instance.exports(store)["dynCall_iiififiii"], store)
dynCall_iiififiiii = partial(instance.exports(store)["dynCall_iiififiiii"], store)
dynCall_iiifii = partial(instance.exports(store)["dynCall_iiifii"], store)
dynCall_iiifiifii = partial(instance.exports(store)["dynCall_iiifiifii"], store)
dynCall_iiifiifiii = partial(instance.exports(store)["dynCall_iiifiifiii"], store)
dynCall_iiifiifiiii = partial(instance.exports(store)["dynCall_iiifiifiiii"], store)
dynCall_iiifiii = partial(instance.exports(store)["dynCall_iiifiii"], store)
dynCall_iiifiiii = partial(instance.exports(store)["dynCall_iiifiiii"], store)
dynCall_iiifiiiii = partial(instance.exports(store)["dynCall_iiifiiiii"], store)
dynCall_iiiifffffi = partial(instance.exports(store)["dynCall_iiiifffffi"], store)
dynCall_iiiifffffii = partial(instance.exports(store)["dynCall_iiiifffffii"], store)
dynCall_iiiiffffi = partial(instance.exports(store)["dynCall_iiiiffffi"], store)
dynCall_iiiiffi = partial(instance.exports(store)["dynCall_iiiiffi"], store)
dynCall_iiiiffii = partial(instance.exports(store)["dynCall_iiiiffii"], store)
dynCall_iiiifi = partial(instance.exports(store)["dynCall_iiiifi"], store)
dynCall_iiiififi = partial(instance.exports(store)["dynCall_iiiififi"], store)
dynCall_iiiifii = partial(instance.exports(store)["dynCall_iiiifii"], store)
dynCall_iiiifiii = partial(instance.exports(store)["dynCall_iiiifiii"], store)
dynCall_iiiifiiii = partial(instance.exports(store)["dynCall_iiiifiiii"], store)
dynCall_iiiifiiiii = partial(instance.exports(store)["dynCall_iiiifiiiii"], store)
dynCall_iiiiifi = partial(instance.exports(store)["dynCall_iiiiifi"], store)
dynCall_iiiiifii = partial(instance.exports(store)["dynCall_iiiiifii"], store)
dynCall_iiiiifiii = partial(instance.exports(store)["dynCall_iiiiifiii"], store)
dynCall_iiiiifiiiiif = partial(instance.exports(store)["dynCall_iiiiifiiiiif"], store)
dynCall_iiiiiifff = partial(instance.exports(store)["dynCall_iiiiiifff"], store)
dynCall_iiiiiifffiiifiii = partial(instance.exports(store)["dynCall_iiiiiifffiiifiii"], store)
dynCall_iiiiiiffiiiiiiiiiffffiii = partial(instance.exports(store)["dynCall_iiiiiiffiiiiiiiiiffffiii"], store)
dynCall_iiiiiiffiiiiiiiiiffffiiii = partial(instance.exports(store)["dynCall_iiiiiiffiiiiiiiiiffffiiii"], store)
dynCall_iiiiiiffiiiiiiiiiiiiiii = partial(instance.exports(store)["dynCall_iiiiiiffiiiiiiiiiiiiiii"], store)
dynCall_iiiiiifi = partial(instance.exports(store)["dynCall_iiiiiifi"], store)
dynCall_iiiiiifiif = partial(instance.exports(store)["dynCall_iiiiiifiif"], store)
dynCall_iiiiiifiii = partial(instance.exports(store)["dynCall_iiiiiifiii"], store)
dynCall_iiiiiiifiif = partial(instance.exports(store)["dynCall_iiiiiiifiif"], store)
dynCall_iiiiij = partial(instance.exports(store)["dynCall_iiiiij"], store)
dynCall_iiiiiji = partial(instance.exports(store)["dynCall_iiiiiji"], store)
dynCall_iiiij = partial(instance.exports(store)["dynCall_iiiij"], store)
dynCall_iiiiji = partial(instance.exports(store)["dynCall_iiiiji"], store)
dynCall_iiiijii = partial(instance.exports(store)["dynCall_iiiijii"], store)
dynCall_iiiijiiii = partial(instance.exports(store)["dynCall_iiiijiiii"], store)
dynCall_iiiijjii = partial(instance.exports(store)["dynCall_iiiijjii"], store)
dynCall_iiiijjiiii = partial(instance.exports(store)["dynCall_iiiijjiiii"], store)
dynCall_iiij = partial(instance.exports(store)["dynCall_iiij"], store)
dynCall_iiiji = partial(instance.exports(store)["dynCall_iiiji"], store)
dynCall_iiijii = partial(instance.exports(store)["dynCall_iiijii"], store)
dynCall_iiijiii = partial(instance.exports(store)["dynCall_iiijiii"], store)
dynCall_iiijji = partial(instance.exports(store)["dynCall_iiijji"], store)
dynCall_iiijjii = partial(instance.exports(store)["dynCall_iiijjii"], store)
dynCall_iiijjiii = partial(instance.exports(store)["dynCall_iiijjiii"], store)
dynCall_iiijjiiii = partial(instance.exports(store)["dynCall_iiijjiiii"], store)
dynCall_iij = partial(instance.exports(store)["dynCall_iij"], store)
dynCall_iiji = partial(instance.exports(store)["dynCall_iiji"], store)
dynCall_iijii = partial(instance.exports(store)["dynCall_iijii"], store)
dynCall_iijiii = partial(instance.exports(store)["dynCall_iijiii"], store)
dynCall_iijiiii = partial(instance.exports(store)["dynCall_iijiiii"], store)
dynCall_iijiiiiii = partial(instance.exports(store)["dynCall_iijiiiiii"], store)
dynCall_iijji = partial(instance.exports(store)["dynCall_iijji"], store)
dynCall_iijjii = partial(instance.exports(store)["dynCall_iijjii"], store)
dynCall_iijjiii = partial(instance.exports(store)["dynCall_iijjiii"], store)
dynCall_iijjji = partial(instance.exports(store)["dynCall_iijjji"], store)
dynCall_ij = partial(instance.exports(store)["dynCall_ij"], store)
dynCall_iji = partial(instance.exports(store)["dynCall_iji"], store)
dynCall_ijii = partial(instance.exports(store)["dynCall_ijii"], store)
dynCall_ijiii = partial(instance.exports(store)["dynCall_ijiii"], store)
dynCall_ijiiii = partial(instance.exports(store)["dynCall_ijiiii"], store)
dynCall_ijj = partial(instance.exports(store)["dynCall_ijj"], store)
dynCall_ijji = partial(instance.exports(store)["dynCall_ijji"], store)
dynCall_j = partial(instance.exports(store)["dynCall_j"], store)
dynCall_jdi = partial(instance.exports(store)["dynCall_jdi"], store)
dynCall_jdii = partial(instance.exports(store)["dynCall_jdii"], store)
dynCall_jfi = partial(instance.exports(store)["dynCall_jfi"], store)
dynCall_ji = partial(instance.exports(store)["dynCall_ji"], store)
dynCall_jid = partial(instance.exports(store)["dynCall_jid"], store)
dynCall_jidi = partial(instance.exports(store)["dynCall_jidi"], store)
dynCall_jidii = partial(instance.exports(store)["dynCall_jidii"], store)
dynCall_jii = partial(instance.exports(store)["dynCall_jii"], store)
dynCall_jiii = partial(instance.exports(store)["dynCall_jiii"], store)
dynCall_jiiii = partial(instance.exports(store)["dynCall_jiiii"], store)
dynCall_jiiiii = partial(instance.exports(store)["dynCall_jiiiii"], store)
dynCall_jiiiiii = partial(instance.exports(store)["dynCall_jiiiiii"], store)
dynCall_jiiiiiiiii = partial(instance.exports(store)["dynCall_jiiiiiiiii"], store)
dynCall_jiiiiiiiiii = partial(instance.exports(store)["dynCall_jiiiiiiiiii"], store)
dynCall_jiiij = partial(instance.exports(store)["dynCall_jiiij"], store)
dynCall_jiiji = partial(instance.exports(store)["dynCall_jiiji"], store)
dynCall_jiji = partial(instance.exports(store)["dynCall_jiji"], store)
dynCall_jijii = partial(instance.exports(store)["dynCall_jijii"], store)
dynCall_jijiii = partial(instance.exports(store)["dynCall_jijiii"], store)
dynCall_jijj = partial(instance.exports(store)["dynCall_jijj"], store)
dynCall_jijji = partial(instance.exports(store)["dynCall_jijji"], store)
dynCall_jji = partial(instance.exports(store)["dynCall_jji"], store)
dynCall_jjii = partial(instance.exports(store)["dynCall_jjii"], store)
dynCall_jjji = partial(instance.exports(store)["dynCall_jjji"], store)
dynCall_jjjji = partial(instance.exports(store)["dynCall_jjjji"], store)
dynCall_vf = partial(instance.exports(store)["dynCall_vf"], store)
dynCall_vff = partial(instance.exports(store)["dynCall_vff"], store)
dynCall_vfff = partial(instance.exports(store)["dynCall_vfff"], store)
dynCall_vffff = partial(instance.exports(store)["dynCall_vffff"], store)
dynCall_vfffffffffiiii = partial(instance.exports(store)["dynCall_vfffffffffiiii"], store)
dynCall_vffffi = partial(instance.exports(store)["dynCall_vffffi"], store)
dynCall_vfffi = partial(instance.exports(store)["dynCall_vfffi"], store)
dynCall_vffi = partial(instance.exports(store)["dynCall_vffi"], store)
dynCall_vfi = partial(instance.exports(store)["dynCall_vfi"], store)
dynCall_vfii = partial(instance.exports(store)["dynCall_vfii"], store)
dynCall_vfiii = partial(instance.exports(store)["dynCall_vfiii"], store)
dynCall_vfiiiii = partial(instance.exports(store)["dynCall_vfiiiii"], store)
dynCall_vif = partial(instance.exports(store)["dynCall_vif"], store)
dynCall_viff = partial(instance.exports(store)["dynCall_viff"], store)
dynCall_vifff = partial(instance.exports(store)["dynCall_vifff"], store)
dynCall_viffff = partial(instance.exports(store)["dynCall_viffff"], store)
dynCall_viffffffffffffiiii = partial(instance.exports(store)["dynCall_viffffffffffffiiii"], store)
dynCall_vifffffffi = partial(instance.exports(store)["dynCall_vifffffffi"], store)
dynCall_viffffffi = partial(instance.exports(store)["dynCall_viffffffi"], store)
dynCall_vifffffi = partial(instance.exports(store)["dynCall_vifffffi"], store)
dynCall_viffffi = partial(instance.exports(store)["dynCall_viffffi"], store)
dynCall_viffffii = partial(instance.exports(store)["dynCall_viffffii"], store)
dynCall_viffffiifffiiiiif = partial(instance.exports(store)["dynCall_viffffiifffiiiiif"], store)
dynCall_viffffiii = partial(instance.exports(store)["dynCall_viffffiii"], store)
dynCall_vifffi = partial(instance.exports(store)["dynCall_vifffi"], store)
dynCall_vifffii = partial(instance.exports(store)["dynCall_vifffii"], store)
dynCall_viffi = partial(instance.exports(store)["dynCall_viffi"], store)
dynCall_viffii = partial(instance.exports(store)["dynCall_viffii"], store)
dynCall_viffiifffffiii = partial(instance.exports(store)["dynCall_viffiifffffiii"], store)
dynCall_viffiii = partial(instance.exports(store)["dynCall_viffiii"], store)
dynCall_viffiiifi = partial(instance.exports(store)["dynCall_viffiiifi"], store)
dynCall_viffiiiif = partial(instance.exports(store)["dynCall_viffiiiif"], store)
dynCall_vifi = partial(instance.exports(store)["dynCall_vifi"], store)
dynCall_vififiii = partial(instance.exports(store)["dynCall_vififiii"], store)
dynCall_vifii = partial(instance.exports(store)["dynCall_vifii"], store)
dynCall_vifiii = partial(instance.exports(store)["dynCall_vifiii"], store)
dynCall_vifiiii = partial(instance.exports(store)["dynCall_vifiiii"], store)
dynCall_vifiiiii = partial(instance.exports(store)["dynCall_vifiiiii"], store)
dynCall_viif = partial(instance.exports(store)["dynCall_viif"], store)
dynCall_viiff = partial(instance.exports(store)["dynCall_viiff"], store)
dynCall_viifff = partial(instance.exports(store)["dynCall_viifff"], store)
dynCall_viiffffffffi = partial(instance.exports(store)["dynCall_viiffffffffi"], store)
dynCall_viiffffffffiii = partial(instance.exports(store)["dynCall_viiffffffffiii"], store)
dynCall_viifffffffi = partial(instance.exports(store)["dynCall_viifffffffi"], store)
dynCall_viiffffffi = partial(instance.exports(store)["dynCall_viiffffffi"], store)
dynCall_viifffffi = partial(instance.exports(store)["dynCall_viifffffi"], store)
dynCall_viiffffi = partial(instance.exports(store)["dynCall_viiffffi"], store)
dynCall_viifffi = partial(instance.exports(store)["dynCall_viifffi"], store)
dynCall_viiffi = partial(instance.exports(store)["dynCall_viiffi"], store)
dynCall_viiffifiii = partial(instance.exports(store)["dynCall_viiffifiii"], store)
dynCall_viiffii = partial(instance.exports(store)["dynCall_viiffii"], store)
dynCall_viiffiifi = partial(instance.exports(store)["dynCall_viiffiifi"], store)
dynCall_viiffiifiii = partial(instance.exports(store)["dynCall_viiffiifiii"], store)
dynCall_viiffiiii = partial(instance.exports(store)["dynCall_viiffiiii"], store)
dynCall_viiffiiiii = partial(instance.exports(store)["dynCall_viiffiiiii"], store)
dynCall_viifi = partial(instance.exports(store)["dynCall_viifi"], store)
dynCall_viififii = partial(instance.exports(store)["dynCall_viififii"], store)
dynCall_viififiii = partial(instance.exports(store)["dynCall_viififiii"], store)
dynCall_viifii = partial(instance.exports(store)["dynCall_viifii"], store)
dynCall_viifiii = partial(instance.exports(store)["dynCall_viifiii"], store)
dynCall_viifiiii = partial(instance.exports(store)["dynCall_viifiiii"], store)
dynCall_viiif = partial(instance.exports(store)["dynCall_viiif"], store)
dynCall_viiifffi = partial(instance.exports(store)["dynCall_viiifffi"], store)
dynCall_viiifffiiij = partial(instance.exports(store)["dynCall_viiifffiiij"], store)
dynCall_viiiffi = partial(instance.exports(store)["dynCall_viiiffi"], store)
dynCall_viiiffii = partial(instance.exports(store)["dynCall_viiiffii"], store)
dynCall_viiifi = partial(instance.exports(store)["dynCall_viiifi"], store)
dynCall_viiififfi = partial(instance.exports(store)["dynCall_viiififfi"], store)
dynCall_viiififi = partial(instance.exports(store)["dynCall_viiififi"], store)
dynCall_viiififii = partial(instance.exports(store)["dynCall_viiififii"], store)
dynCall_viiifii = partial(instance.exports(store)["dynCall_viiifii"], store)
dynCall_viiifiii = partial(instance.exports(store)["dynCall_viiifiii"], store)
dynCall_viiifiiiii = partial(instance.exports(store)["dynCall_viiifiiiii"], store)
dynCall_viiiif = partial(instance.exports(store)["dynCall_viiiif"], store)
dynCall_viiiiffffffi = partial(instance.exports(store)["dynCall_viiiiffffffi"], store)
dynCall_viiiifffffi = partial(instance.exports(store)["dynCall_viiiifffffi"], store)
dynCall_viiiiffffii = partial(instance.exports(store)["dynCall_viiiiffffii"], store)
dynCall_viiiifffi = partial(instance.exports(store)["dynCall_viiiifffi"], store)
dynCall_viiiiffiii = partial(instance.exports(store)["dynCall_viiiiffiii"], store)
dynCall_viiiifi = partial(instance.exports(store)["dynCall_viiiifi"], store)
dynCall_viiiififfi = partial(instance.exports(store)["dynCall_viiiififfi"], store)
dynCall_viiiifii = partial(instance.exports(store)["dynCall_viiiifii"], store)
dynCall_viiiifiifi = partial(instance.exports(store)["dynCall_viiiifiifi"], store)
dynCall_viiiifiii = partial(instance.exports(store)["dynCall_viiiifiii"], store)
dynCall_viiiifiiii = partial(instance.exports(store)["dynCall_viiiifiiii"], store)
dynCall_viiiifiiiii = partial(instance.exports(store)["dynCall_viiiifiiiii"], store)
dynCall_viiiifiiiiif = partial(instance.exports(store)["dynCall_viiiifiiiiif"], store)
dynCall_viiiifiiiiiiii = partial(instance.exports(store)["dynCall_viiiifiiiiiiii"], store)
dynCall_viiiiif = partial(instance.exports(store)["dynCall_viiiiif"], store)
dynCall_viiiiiffi = partial(instance.exports(store)["dynCall_viiiiiffi"], store)
dynCall_viiiiiffii = partial(instance.exports(store)["dynCall_viiiiiffii"], store)
dynCall_viiiiifi = partial(instance.exports(store)["dynCall_viiiiifi"], store)
dynCall_viiiiifiii = partial(instance.exports(store)["dynCall_viiiiifiii"], store)
dynCall_viiiiiif = partial(instance.exports(store)["dynCall_viiiiiif"], store)
dynCall_viiiiiifddfiii = partial(instance.exports(store)["dynCall_viiiiiifddfiii"], store)
dynCall_viiiiiiffffiii = partial(instance.exports(store)["dynCall_viiiiiiffffiii"], store)
dynCall_viiiiiifiifiii = partial(instance.exports(store)["dynCall_viiiiiifiifiii"], store)
dynCall_viiiiiifjjfiii = partial(instance.exports(store)["dynCall_viiiiiifjjfiii"], store)
dynCall_viiiiiiifddfii = partial(instance.exports(store)["dynCall_viiiiiiifddfii"], store)
dynCall_viiiiiiiffffii = partial(instance.exports(store)["dynCall_viiiiiiiffffii"], store)
dynCall_viiiiiiifiifii = partial(instance.exports(store)["dynCall_viiiiiiifiifii"], store)
dynCall_viiiiiiifjjfii = partial(instance.exports(store)["dynCall_viiiiiiifjjfii"], store)
dynCall_viiiiiiiiiiifii = partial(instance.exports(store)["dynCall_viiiiiiiiiiifii"], store)
dynCall_viiiiiji = partial(instance.exports(store)["dynCall_viiiiiji"], store)
dynCall_viiiij = partial(instance.exports(store)["dynCall_viiiij"], store)
dynCall_viiiijii = partial(instance.exports(store)["dynCall_viiiijii"], store)
dynCall_viiiijiiii = partial(instance.exports(store)["dynCall_viiiijiiii"], store)
dynCall_viiij = partial(instance.exports(store)["dynCall_viiij"], store)
dynCall_viiiji = partial(instance.exports(store)["dynCall_viiiji"], store)
dynCall_viiijji = partial(instance.exports(store)["dynCall_viiijji"], store)
dynCall_viij = partial(instance.exports(store)["dynCall_viij"], store)
dynCall_viiji = partial(instance.exports(store)["dynCall_viiji"], store)
dynCall_viijii = partial(instance.exports(store)["dynCall_viijii"], store)
dynCall_viijiii = partial(instance.exports(store)["dynCall_viijiii"], store)
dynCall_viijiijiii = partial(instance.exports(store)["dynCall_viijiijiii"], store)
dynCall_viijijii = partial(instance.exports(store)["dynCall_viijijii"], store)
dynCall_viijijiii = partial(instance.exports(store)["dynCall_viijijiii"], store)
dynCall_viijijj = partial(instance.exports(store)["dynCall_viijijj"], store)
dynCall_viijj = partial(instance.exports(store)["dynCall_viijj"], store)
dynCall_viijji = partial(instance.exports(store)["dynCall_viijji"], store)
dynCall_viijjii = partial(instance.exports(store)["dynCall_viijjii"], store)
dynCall_viijjiii = partial(instance.exports(store)["dynCall_viijjiii"], store)
dynCall_viijjji = partial(instance.exports(store)["dynCall_viijjji"], store)
dynCall_vij = partial(instance.exports(store)["dynCall_vij"], store)
dynCall_viji = partial(instance.exports(store)["dynCall_viji"], store)
dynCall_vijii = partial(instance.exports(store)["dynCall_vijii"], store)
dynCall_vijiii = partial(instance.exports(store)["dynCall_vijiii"], store)
dynCall_vijiiii = partial(instance.exports(store)["dynCall_vijiiii"], store)
dynCall_vijiji = partial(instance.exports(store)["dynCall_vijiji"], store)
dynCall_vijijji = partial(instance.exports(store)["dynCall_vijijji"], store)
dynCall_vijji = partial(instance.exports(store)["dynCall_vijji"], store)
dynCall_vijjii = partial(instance.exports(store)["dynCall_vijjii"], store)
dynCall_vijjji = partial(instance.exports(store)["dynCall_vijjji"], store)
dynCall_vji = partial(instance.exports(store)["dynCall_vji"], store)
dynCall_vjii = partial(instance.exports(store)["dynCall_vjii"], store)
dynCall_vjiiii = partial(instance.exports(store)["dynCall_vjiiii"], store)
dynCall_vjji = partial(instance.exports(store)["dynCall_vjji"], store)

print('debug')