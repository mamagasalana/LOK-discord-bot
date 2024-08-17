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

class JSSYS:
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