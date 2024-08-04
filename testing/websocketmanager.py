import websocket
import os

class customWebSocket(websocket.WebSocketApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bufferedAmount = 0

    # Override
    def send(self, data, opcode=websocket.ABNF.OPCODE_TEXT):
        super().send(data, opcode)
        self.bufferedAmount += len(data)

class WebSocketClientManager:
    def __init__(self, o):
        self.webSocketInstances = {} 
        self.o = o

    @property
    def nextInstanceId(self):
        return len(self.webSocketInstances) +1
    
    def set(self, socket):
        self.webSocketInstances[self.nextInstanceId] =socket
        return self.nextInstanceId

    def get(self, id):
        return self.webSocketInstances[id]

    def _callOnOpen(self, onOpen, id):
        self.o.dynCall_vi(onOpen, id);

    def _callOnBinary(self, onBinary, id, data):
        byteArray = bytearray(data)
        buffer = self.o._malloc(len(byteArray))
        self.o.HEAPU8.set(byteArray, buffer)
        self.o.dynCall_viii(onBinary, id, buffer, len(byteArray))

    def _callOnText(self, onText, id, data):
        length = self.o.lengthBytesUTF8(data) + 1
        buffer = self.o._malloc(length)
        self.o.stringToUTF8Array(data, self.o.HEAPU8, buffer, length)
        self.o.dynCall_vii(onText, id, buffer)

    def _callOnClose(self, onClose, id, code, reason):
        length = self.o.lengthBytesUTF8(reason) + 1
        buffer = self.o._malloc(length)
        self.o.stringToUTF8Array(reason, self.o.HEAPU8, buffer, length)
        self.o.dynCall_viii(onClose, id, code, buffer)

    def  _callOnError(self, errCallback, id, reason):
        length = self.o.lengthBytesUTF8(reason) + 1
        buffer = self.o._malloc(length)
        self.o.stringToUTF8Array(reason, self.o.HEAPU8, buffer, length)
        self.o.dynCall_vii(errCallback, id, buffer)


Module = {
    "preloadPlugins": [],
    "logReadFiles": False,
    "stdin": None,
    "stdout": None,
    "stderr": None,
    "read": lambda url: open(url, 'r').read()
}

MEMFS = {
    "mount": lambda mount: {"mount": mount, "node_ops": {}, "stream_ops": {}}
}
IDBFS = NODEFS = WORKERFS = MEMFS

def UTF8ArrayToString(array, idx):
    return ''.join(chr(b) for b in array[idx:] if b != 0)

def stringToUTF8Array(string, array, idx, maxBytesToWrite):
    for i, char in enumerate(string[:maxBytesToWrite - 1]):
        array[idx + i] = ord(char)
    array[idx + len(string[:maxBytesToWrite - 1])] = 0
    return len(string[:maxBytesToWrite - 1]) + 1

def intArrayFromString(string, nullTerminated=False):
    result = [ord(c) for c in string]
    if nullTerminated:
        result.append(0)
    return result

def time():
    import time
    return int(time.time())

class FS:
    def __init__(self):
        self.streams = []

    def getStream(self, fd):
        return self.streams[fd]

class SYSCALLS:
    def __init__(self, o):
        self.varargs =  0
        self.o = o

    def getStreamFromFD(self):
        stream = FS.getStream(self.get())
        return stream

    def get(self):
        self.varargs += 4
        ret = self.o.HEAP32[self.varargs - 4 >> 2]
        return ret
