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


class SYSCALLS:
    DEFAULT_POLLMASK = 5
    mappings = {}
    umask = 0o777

    @staticmethod
    def calculateAt(dirfd, path):
        if not path.startswith('/'):
            if dirfd == -100:
                dir = FS.cwd()
            else:
                dirstream = FS.getStream(dirfd)
                if not dirstream:
                    raise FS.ErrnoError(errno.EBADF)
                dir = dirstream.name
            path = os.path.join(dir, path)
        return path

    @staticmethod
    def doStat(func, path, buf):
        try:
            stat_res = func(path)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                return -errno.ENOTDIR
            raise

        buf[0] = stat_res.st_dev
        buf[1] = 0
        buf[2] = stat_res.st_ino
        buf[3] = stat_res.st_mode
        buf[4] = stat_res.st_nlink
        buf[5] = stat_res.st_uid
        buf[6] = stat_res.st_gid
        buf[7] = stat_res.st_rdev
        buf[8] = 0
        buf[9] = stat_res.st_size
        buf[10] = 4096
        buf[11] = stat_res.st_blocks
        buf[12] = int(stat_res.st_atime)
        buf[13] = 0
        buf[14] = int(stat_res.st_mtime)
        buf[15] = 0
        buf[16] = int(stat_res.st_ctime)
        buf[17] = 0
        buf[18] = stat_res.st_ino
        return 0

    @staticmethod
    def doMsync(addr, stream, len, flags):
        buffer = ctypes.string_at(addr, len)
        FS.msync(stream, buffer, 0, len, flags)

    @staticmethod
    def doMkdir(path, mode):
        path = os.path.normpath(path)
        if path.endswith('/'):
            path = path[:-1]
        FS.mkdir(path, mode, 0)
        return 0

    @staticmethod
    def doMknod(path, mode, dev):
        if (mode & stat.S_IFMT) not in [stat.S_IFREG, stat.S_IFCHR, stat.S_IFBLK, stat.S_IFIFO, stat.S_IFSOCK]:
            return -errno.EINVAL
        FS.mknod(path, mode, dev)
        return 0

    @staticmethod
    def doReadlink(path, buf, bufsize):
        if bufsize <= 0:
            return -errno.EINVAL
        ret = FS.readlink(path)
        length = min(bufsize, len(ret))
        buf[:length] = ret.encode('utf-8')
        return length

    @staticmethod
    def doAccess(path, amode):
        if amode & ~7:
            return -errno.EINVAL
        node = FS.lookupPath(path, follow=True)['node']
        perms = ""
        if amode & os.R_OK:
            perms += "r"
        if amode & os.W_OK:
            perms += "w"
        if amode & os.X_OK:
            perms += "x"
        if perms and FS.nodePermissions(node, perms):
            return -errno.EACCES
        return 0

    @staticmethod
    def doDup(path, flags, suggestFD):
        suggest = FS.getStream(suggestFD)
        if suggest:
            suggest.close()
        return os.dup2(os.open(path, flags), suggestFD)

    @staticmethod
    def doReadv(stream, iov, iovcnt, offset):
        ret = 0
        for i in range(iovcnt):
            ptr = iov[i][0]
            length = iov[i][1]
            curr = FS.read(stream, HEAP8, ptr, length, offset)
            if curr < 0:
                return -1
            ret += curr
            if curr < length:
                break
        return ret

    @staticmethod
    def doWritev(stream, iov, iovcnt, offset):
        ret = 0
        for i in range(iovcnt):
            ptr = iov[i][0]
            length = iov[i][1]
            curr = FS.write(stream, HEAP8, ptr, length, offset)
            if curr < 0:
                return -1
            ret += curr
        return ret

    varargs = 0

    @staticmethod
    def get(varargs):
        SYSCALLS.varargs += 4
        return HEAP32[SYSCALLS.varargs - 4 >> 2]

    @staticmethod
    def getStr():
        return ctypes.string_at(SYSCALLS.get()).decode('utf-8')

    @staticmethod
    def getStreamFromFD():
        stream = FS.getStream(SYSCALLS.get())
        if not stream:
            raise FS.ErrnoError(errno.EBADF)
        return stream

    @staticmethod
    def getSocketFromFD():
        # Placeholder for getting socket from FD
        return None

    @staticmethod
    def getSocketAddress(allowNull):
        addrp = SYSCALLS.get()
        addrlen = SYSCALLS.get()
        if allowNull and addrp == 0:
            return None
        # Placeholder for reading sockaddr
        return {'addr': '127.0.0.1', 'port': 80}

    @staticmethod
    def get64():
        low = SYSCALLS.get()
        high = SYSCALLS.get()
        assert high == 0 or high == -1
        return low

    @staticmethod
    def getZero():
        assert SYSCALLS.get() == 0