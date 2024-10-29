import websocket
import os
import numpy as np
from pathlib import Path
import io
import logging
import codecs
import json

class EarlyExit(Exception):
    pass

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
        super().__init__(fd, mode='r+b')
        self.fd = fd
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
    
    def write_contents(self, buffer, offset, length):
        self.write(buffer[offset: offset+length])
        return self.tell()
        
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

class CANVAS:
    canvasSharedPtr =  None
    offscreenCanvas =  None 
    controlTransferredOffscreen =  None
    width = 300
    height = 150 

class GL:
    def __init__(self):
        self.lastError = 0
        self.stringCache = {}
        self.stringiCache = {}
        self.programInfos = {}

        self.contexts = []
        self.buffers = []
        self.programs = []
        self.uniforms = []
        self.shaders = []
        self.queries = []
        self.samplers = []
        self.textures = []
        self.framebuffers = []
        self.renderbuffers = []
        self.transformfeedbacks = []
        self.vaos = []
        self.syncs = []

        self.currentContext = None
        self.contexts_ext  = {
            'WEBGL_compressed_texture_s3tc_srgb' : 'WebGLCompressedTextureS3TCsRGB',
            'EXT_color_buffer_float' : 'EXTColorBufferFloat',
            }
        self.byteSizeByTypeRoot=  5120
        self.byteSizeByType = [1, 1, 2, 2, 4, 4, 4, 2, 3, 4, 8]
        self.packAlignment = 4
        self.unpackAlignment = 4
        self.counter = 1

        self.text_param = {}

    def ctx_getParameter(self, k):
        
        ref = {
            3379: 16384,
            7936: 'WebKit',
            7937: 'WebKit WebGL',
            7938: 'WebGL 2.0 (OpenGL ES 3.0 Chromium)',
            35724: 'WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)',
            34467: np.array([33776, 33777, 33778, 33779, 35916, 35917, 35918, 35919], dtype=np.uint32),
            34016: 33984,
            36183: 16,
            35661: 32,
            35660: 16,
            34076: 16384,
            35071: 2048,
            34047: 16,
            36063: 8,
            34024: 16384,
            35658: 16384,
            35376: 65536,
            35375: 24,
            35380: 256,
            34921: 16,
            3410: 8,
            3411: 8,
            3412: 8,
            3413: 8,
            3414: 24,
            3415: 8,
            32937: 0,
            32936: 0,
        }

        if k not in ref:
            logging.error('ctx_getParameter %s not found' % k)
        ret = ref.get(k)
        if ret is None:
            logging.warning(f'ctx_getParameter {k} is None')
            
        return ret

    def ctx_getInternalformatParameter(self, *args):
        ref = {
            (36161, 35907, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 33321, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 33323, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 32849, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 32856, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 36756, 32937): None, 
            (36161, 36757, 32937): None, 
            (36161, 36759, 32937): None, 
            (36161, 33330, 32937): np.array([], dtype=np.uint32), 
            (36161, 33336, 32937): np.array([], dtype=np.uint32), 
            (36161, 36220, 32937): np.array([], dtype=np.uint32), 
            (36161, 33329, 32937): np.array([], dtype=np.uint32), 
            (36161, 33335, 32937): np.array([], dtype=np.uint32), 
            (36161, 36238, 32937): np.array([], dtype=np.uint32), 
            (36161, 33322, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 33324, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 32859, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 36760, 32937): None, 
            (36161, 36761, 32937): None, 
            (36161, 36763, 32937): None, 
            (36161, 33332, 32937): np.array([], dtype=np.uint32), 
            (36161, 33338, 32937): np.array([], dtype=np.uint32), 
            (36161, 36214, 32937): np.array([], dtype=np.uint32), 
            (36161, 33331, 32937): np.array([], dtype=np.uint32), 
            (36161, 33337, 32937): np.array([], dtype=np.uint32), 
            (36161, 36232, 32937): np.array([], dtype=np.uint32), 
            (36161, 33334, 32937): np.array([], dtype=np.uint32), 
            (36161, 33340, 32937): np.array([], dtype=np.uint32), 
            (36161, 36208, 32937): np.array([], dtype=np.uint32), 
            (36161, 33333, 32937): np.array([], dtype=np.uint32), 
            (36161, 33339, 32937): np.array([], dtype=np.uint32), 
            (36161, 36226, 32937): np.array([], dtype=np.uint32), 
            (36161, 33325, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 33327, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 34842, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 33326, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 33328, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 34836, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 32854, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 36194, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 32855, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 35898, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 32857, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 33189, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 33190, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 35056, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 36012, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 36013, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32), 
            (36161, 36168, 32937): np.array([16,  8,  4,  2,  1], dtype=np.uint32)}

        if not args in ref:
            logging.error(f'ctx_getInternalformatParameter {args} not found')
        
        ret = ref.get(args)
        if ret is None:
            logging.warning(f'ctx_getInternalformatParameter {args} is None')
            
        return ret
    
    def ctx_getProgramParameter(self, *args):
        ref = {
            35714: True,
            35382: 0,
            (36, 35718): 11,
            (75, 35718): 5,
        }

        ret = 0
        if (args[0]['name'], args[-1]) in ref:
            return ref[(args[0]['name'], args[-1])]
        else:
            if not args[-1] in ref:
                logging.error(f'ctx_getProgramParameter {args} not found')
            return ref.get(args[-1], ret)
    
    def ctx_getUniformLocation(self, *args):
        return {}
    
    def ctx_fenceSync(self, *args):
        return {}
    
    def ctx_getShaderParameter(self, *args):
        ref = {
            35713: True,
        }
        return ref[args[-1]]

    def ctx_getShaderSource(self, *args):
        logging.error('ctx getShaderSource not implemented')

    def ctx_getActiveAttrib(self, *args):
        logging.error('ctx_getActiveAttrib not implemented')

    def ctx_getActiveUniform(self, *args):
        ref = {}
        ref[36] = [{'size': 1, 'type': 35666, 'name': '_ScreenParams'},
            {'size': 4, 'type': 35666, 'name': 'hlslcc_mtx4x4unity_ObjectToWorld[0]'},
            {'size': 4, 'type': 35666, 'name': 'hlslcc_mtx4x4glstate_matrix_projection[0]'},
            {'size': 4, 'type': 35666, 'name': 'hlslcc_mtx4x4unity_MatrixVP[0]'},
            {'size': 1, 'type': 35666, 'name': '_Color'},
            {'size': 1, 'type': 35666, 'name': '_ClipRect'},
            {'size': 1, 'type': 35666, 'name': '_MainTex_ST'},
            {'size': 1, 'type': 5126, 'name': '_UIMaskSoftnessX'},
            {'size': 1, 'type': 5126, 'name': '_UIMaskSoftnessY'},
            {'size': 1, 'type': 35666, 'name': '_TextureSampleAdd'},
            {'size': 1, 'type': 35678, 'name': '_MainTex'},]
        
        ref[75] = [
             {'size': 4, 'type': 35666, 'name': 'hlslcc_mtx4x4unity_ObjectToWorld[0]'},
             {'size': 4, 'type': 35666, 'name': 'hlslcc_mtx4x4unity_MatrixVP[0]'},
             {'size': 1, 'type': 35666, 'name': '_MainTex_ST'},
             {'size': 1, 'type': 35666, 'name': '_Color'},
             {'size': 1, 'type': 35678, 'name': '_MainTex'},]
        
        return ref[args[0]['name']][args[-1]]
    
    def ctx_getActiveUniformBlockName(self, *args):
        logging.error('ctx_getActiveUniformBlockName not implemented')

    def ctx_setTexParameter(self, target, pname, params):
        self.text_param[(target, pname)] = params
    
    def ctx_getTexParameter(self, *args):
        if not args in self.text_param:
            logging.warning(f'ctx_getTexParameter {args} not found')
        
        ret = self.text_param.get(args, 0)
        return ret
    
    def getNewId(self, table: list):
        ret = self.counter
        self.counter +=1
        for _ in range( len(table), ret):
            table.append(None)
        
        #append one more to create that length
        table.append(None)
        logging.info('getNewId: %s' % ret)
        return ret

class JSException(Exception):
    def __init__(self, ptr, ex_type, destructor):
        super().__init__(f'throw {ptr}')
        self.ptr = ptr
        self.adjusted = ptr
        self.type = ex_type
        self.destructor = destructor
        self.refcount = 0
        self.caught = False
        self.rethrown = False

if __name__ == '__main__':
    # print(bool(CANVAS.controlTransferredOffscreen))
    try:
        raise JSException(1,2,3)
    except Exception as e:
        print(str(e))
