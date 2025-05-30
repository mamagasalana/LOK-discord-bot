from wasmtime import Config, Store, Engine, Module, FuncType, Func, ValType, Instance, Limits, MemoryType, Global, GlobalType, Val, Memory, Table, TableType
from functools import partial
import numpy as np
import codecs
import math
import logging

# local modules
from wasmbase2 import wasm_base

class LOK_JS2PY(wasm_base):
    def __init__(self, wasmfile= "testout.wasm"):
        super().__init__()
        if 1:
            self.wasmfile = wasmfile
            self.config = Config()
            self.config.wasm_multi_value = True
            self.engine = Engine()

            # Load the Wasm module
            self.wasm_module = Module.from_file(self.engine, wasmfile)
            self.store = Store(self.engine)
            # Create memory
            limits = Limits(512, None)  # Replace None with maximum size if needed
            memory_type = MemoryType(limits)
            self.memory = Memory(self.store, memory_type)

            # Create table
            limits = Limits(181773, 181773)
            table_type = TableType(ValType.funcref(), limits)
            table = Table(self.store, table_type, None)

            mutable = False  # Mutable
            global_type32 = GlobalType(ValType.i32(), mutable)
            global_type64 = GlobalType(ValType.f64(), mutable)
            # Create globals
            self.global_tableBase = Global(self.store, global_type32, Val.i32(0))
            self.global_DYNAMICTOP_PTR = Global(self.store, global_type32, Val.i32(self.DYNAMICTOP_PTR))
            self.global_STACKTOP = Global(self.store, global_type32, Val.i32(self.STACKTOP))
            self.global_STACK_MAX = Global(self.store, global_type32, Val.i32(self.STACK_MAX))

            
            wasm_args = [self.memory, 
                    table, 
                    self.global_tableBase,
                    self.global_DYNAMICTOP_PTR,
                    self.global_STACKTOP,
                    self.global_STACK_MAX,
                    Global(self.store, global_type64, Val.f64(float('nan'))),
                    Global(self.store, global_type64, Val.f64(float('inf'))),
                    Func(self.store, FuncType([ValType.f64(), ValType.f64()], [ValType.f64()]), pow),
                    ] + list(self.import_object.values())

            self.instance = Instance(self.store, self.wasm_module, wasm_args)
            self.export_wasm_func()

            self.tm_timezone = 5948960

    def buffer(self, dtype):
        return np.frombuffer(self.memory.get_buffer_ptr(self.store), dtype=dtype)
    
    @property
    def HEAP8(self):
        return self.buffer(np.int8)
    
    @property
    def HEAP16(self):
        return self.buffer(np.int16)
    
    @property
    def HEAP32(self):
        return self.buffer(np.int32)

    @property
    def HEAP64(self):
        return self.buffer(np.int64)
    
    @property
    def HEAPU8(self):
        return self.buffer(np.uint8)
    
    @property
    def HEAPU16(self):
        return self.buffer(np.uint16)

    @property
    def HEAPU32(self):
        return self.buffer(np.uint32)

    @property
    def HEAPF32(self):
        return self.buffer(np.float32)
    
    @property
    def HEAPF64(self):
        return self.buffer(np.float64)


    
    def lengthBytesUTF8(self, s):
        return len(s.encode('utf-8')) 

    def stringToUTF8(self, s, outPtr, maxBytesToWrite):
        return self.stringToUTF8Array(s, self.HEAPU8, outPtr, maxBytesToWrite)
    
    def stringToUTF8Array(self, s, outU8Array, outIdx, maxBytesToWrite):
        if not (maxBytesToWrite > 0):
            return 0

        utf8_bytes = s.encode('utf-8')
        bytes_to_copy = min(len(utf8_bytes), maxBytesToWrite - 1)  # Leave space for the null terminator

        # Copy the bytes to the output array
        to_be_input= np.frombuffer(utf8_bytes[:bytes_to_copy], dtype=np.uint8) 
        for idx, inp in enumerate(to_be_input, start=outIdx):
            outU8Array[idx] = int(inp)
        # outU8Array[outIdx:outIdx + bytes_to_copy] = np.frombuffer(utf8_bytes[:bytes_to_copy], dtype=np.uint8)
        outU8Array[outIdx + bytes_to_copy] = 0  # Null terminator

        return bytes_to_copy

    def UTF8ToString(self,ptr):
        return UTF8ArrayToString(self.HEAPU8, ptr)

    def Pointer_stringify(self, ptr, length=None):
        if (length == 0 or  not ptr):
            return ""
        hasUtf = 0
        i = 0
        while True:
            t = self.HEAPU8[ptr + i]
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
                curr = "".join(chr(self.HEAPU8[ptr + j]) for j in range(min(length, MAX_CHUNK)))
                ret += curr
                ptr += MAX_CHUNK
                length -= MAX_CHUNK
            return ret
        
        return self.UTF8ToString(ptr)

    def allocateUTF8(self, _in):
        size = self.lengthBytesUTF8(_in) + 1
        ret = self._malloc(size)
        if ret:
            self.stringToUTF8Array(_in, self.HEAP8, ret, size)
        return ret

    def allocateUTF8OnStack(self, _in):
        size = self.lengthBytesUTF8(_in) +1
        ret = self.stackAlloc(size)
        self.stringToUTF8Array(_in, self.HEAP8, ret, size)
        return ret

    def alignUp(self, x, multiple):
        if x % multiple > 0:
            x += multiple - (x % multiple)
        return x

    def reallocBuffer(self, size):
        PAGE_MULTIPLE = self.WASM_PAGE_SIZE 
        size = self.alignUp(size, PAGE_MULTIPLE)
        oldSize = self.HEAP8.nbytes

        ret = self.memory.grow(self.store, (size - oldSize) // PAGE_MULTIPLE)
        return True
            
if __name__ =='__main__':
    import os
    try:
        os.remove('app.log')
    except:
        pass
    logging.basicConfig(
        filename='app.log',          # Log file name
        level=logging.INFO,          # Minimum log level to capture
        format='%(asctime)s - %(levelname)s - %(message)s'  # Optional format
    )

    lok = LOK_JS2PY()
    lok.START_DEBUG=True

    if 1:
        #default
        with open('new2.bin', 'rb') as ifile:
            heap8 = np.frombuffer(ifile.read(), dtype=np.uint8)

        lok.reallocBuffer(heap8.size)
        np.copyto(lok.HEAP8, heap8)
        lok.dynCall_v(876)
    else:
        with open('predebug.bin', 'rb') as ifile:
            heap8 = np.frombuffer(ifile.read(), dtype=np.uint8)

        lok.reallocBuffer(heap8.size)
        np.copyto(lok.HEAP8, heap8)
        try:
            lok.part1( 0, 35777328, 158712992, 5950017)
        except:
            logging.error('check trace', exc_info=True)


    # lok.invoke_iiii(6063, 269091040,  269781120, 0)
    #decryption
    # input: a, b, c
    # input is gzip >> base64.decode
    # starting index of input -16

    # c is always 0

    # return : the index of the output -16
    # {0: 279504540, 1: 48, 2: 261487248, 3: 35, 4: 0}
    # #279504540 in index
    # # 261487248 out index
    # # 48 size of regionhash
    # # 35 size of output? always 35?

    # output_idx = lok.decryption(279504540,48, 261487248, 35, 0)


    with open('after4.bin', 'wb') as ifile:
        ifile.write(bytes(lok.HEAP8))
    print('debug')