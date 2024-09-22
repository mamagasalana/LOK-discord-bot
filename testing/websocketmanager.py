import websocket
import os
import numpy as np
from pathlib import Path
import io
import logging
import codecs

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

class FS(io.FileIO):
    def __init__(self, fd, path, tty=False):
        super().__init__(fd)
        self.path = path
        if tty:
            self.tty = {'input': [], 'output': []}
        else:
            self.tty = None

    def read_to_buffer(self, buffer, offset, length):
        contents = self.read(length)
        contents_np = np.frombuffer(contents, dtype=np.uint8)
        size = len(contents)
        buffer[offset:offset + size] = contents_np
        return size
        
    def write_to_buffer(self, buffer, offset, length):
        for i in range(length):
            val = buffer[offset + i]
            if not val or val == 10:
                logging.info(UTF8ArrayToString(self.tty['output'], 0))
                self.tty['output'] = []
            else:
                if val != 0:
                    self.tty['output'].append(val)
        return i+1
    
class JSSYS:
    def __init__(self, o):
        self.varargs =  0
        self.o = o
        self.mappings = {}

    def getStreamFromFD(self) -> FS:
        stream = self.o.streams[self.get()]
        # logging.info('JSSYS %s ' % stream)
        return stream

    def get(self):
        self.varargs += 4
        ret = self.o.HEAP32[self.varargs - 4 >> 2]
        # logging.info('JSSYS %s ' % ret)
        return int(ret)

    def getStr(self):
        ret = self.o.Pointer_stringify(self.get())
        # logging.info('JSSYS %s ' % ret)
        fx = lambda x : os.path.join(*['testing' , 'js_testing', 'JS_MOUNT', x])
        if ret.startswith('/'):
            ret = ret[1:]
        return fx(ret)
          
    def doReadv(self, stream: FS, iov, iovcnt):
        ret = 0

        for i in range(iovcnt):
            ptr = self.o.HEAP32[(iov + i * 8) >> 2]
            length = self.o.HEAP32[(iov + (i * 8 + 4)) >> 2]
            curr = stream.read_to_buffer(self.o.HEAP8, ptr, length)
            if curr < 0:
                return -1
            
            ret += curr
            
            if curr < length:
                break

        return ret
    
    def doWritev(self, stream: FS, iov, iovcnt):
        ret = 0

        for i in range(iovcnt):
            ptr = self.o.HEAP32[(iov + i * 8) >> 2]
            length = self.o.HEAP32[(iov + (i * 8 + 4)) >> 2]
            curr = stream.write_to_buffer(self.o.HEAP8, ptr, length)
            if curr < 0:
                return -1
            
            ret += curr
            
        return ret

def UTF8ArrayToString(u8Array, idx: int):
    UTF8Decoder = codecs.getincrementaldecoder('utf-8')()
    endPtr = idx
    while len(u8Array)>endPtr and u8Array[endPtr]:
        endPtr += 1

    return UTF8Decoder.decode(bytes(u8Array[idx:endPtr]))

class ERRNO_CODES:
    EPERM=1
    ENOENT=2
    ESRCH=3
    EINTR=4
    EIO=5
    ENXIO=6
    E2BIG=7
    ENOEXEC=8
    EBADF=9
    ECHILD=10
    EAGAIN=11
    EWOULDBLOCK=11
    ENOMEM=12
    EACCES=13
    EFAULT=14
    ENOTBLK=15
    EBUSY=16
    EEXIST=17
    EXDEV=18
    ENODEV=19
    ENOTDIR=20
    EISDIR=21
    EINVAL=22
    ENFILE=23
    EMFILE=24
    ENOTTY=25
    ETXTBSY=26
    EFBIG=27
    ENOSPC=28
    ESPIPE=29
    EROFS=30
    EMLINK=31
    EPIPE=32
    EDOM=33
    ERANGE=34
    ENOMSG=42
    EIDRM=43
    ECHRNG=44
    EL2NSYNC=45
    EL3HLT=46
    EL3RST=47
    ELNRNG=48
    EUNATCH=49
    ENOCSI=50
    EL2HLT=51
    EDEADLK=35
    ENOLCK=37
    EBADE=52
    EBADR=53
    EXFULL=54
    ENOANO=55
    EBADRQC=56
    EBADSLT=57
    EDEADLOCK=35
    EBFONT=59
    ENOSTR=60
    ENODATA=61
    ETIME=62
    ENOSR=63
    ENONET=64
    ENOPKG=65
    EREMOTE=66
    ENOLINK=67
    EADV=68
    ESRMNT=69
    ECOMM=70
    EPROTO=71
    EMULTIHOP=72
    EDOTDOT=73
    EBADMSG=74
    ENOTUNIQ=76
    EBADFD=77
    EREMCHG=78
    ELIBACC=79
    ELIBBAD=80
    ELIBSCN=81
    ELIBMAX=82
    ELIBEXEC=83
    ENOSYS=38
    ENOTEMPTY=39
    ENAMETOOLONG=36
    ELOOP=40
    EOPNOTSUPP=95
    EPFNOSUPPORT=96
    ECONNRESET=104
    ENOBUFS=105
    EAFNOSUPPORT=97
    EPROTOTYPE=91
    ENOTSOCK=88
    ENOPROTOOPT=92
    ESHUTDOWN=108
    ECONNREFUSED=111
    EADDRINUSE=98
    ECONNABORTED=103
    ENETUNREACH=101
    ENETDOWN=100
    ETIMEDOUT=110
    EHOSTDOWN=112
    EHOSTUNREACH=113
    EINPROGRESS=115
    EALREADY=114
    EDESTADDRREQ=89
    EMSGSIZE=90
    EPROTONOSUPPORT=93
    ESOCKTNOSUPPORT=94
    EADDRNOTAVAIL=99
    ENETRESET=102
    EISCONN=106
    ENOTCONN=107
    ETOOMANYREFS=109
    EUSERS=87
    EDQUOT=122
    ESTALE=116
    ENOTSUP=95
    ENOMEDIUM=123
    EILSEQ=84
    EOVERFLOW=75
    ECANCELED=125
    ENOTRECOVERABLE=131
    EOWNERDEAD=130
    ESTRPIPE=86

class JSModule:
    webglContextAttributes = {
        'premultipliedAlpha': False,  # Example value
        'preserveDrawingBuffer': False  # Example value
    }
    shouldQuit = None  # Example initialization

ASM_CONSTS = [
    lambda: JSModule.webglContextAttributes.get('premultipliedAlpha'),
    lambda: JSModule.webglContextAttributes.get('preserveDrawingBuffer'),
    lambda: JSModule.shouldQuit is not None,
    lambda: logging.error('ASM_CONSTS3 not defined')
]

if __name__ == '__main__':
    print(ASM_CONSTS[1]())
