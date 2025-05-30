import sys

sys.path.append('testing')

import os
import re
import math
from wasmtime import Func, FuncType, ValType, Store
from functools import wraps, partial
import logging
import datetime
import time
from websocketmanager import customWebSocket, JSSYS,ERRNO_CODES, FS, ASM_CONSTS, UTF8ArrayToString, CANVAS, GL, JSException, WebSocketClientManager, EarlyExit


def log_wasm(k,v):
    logging.info(f"from funcname {k}, {v}")

import numpy as np
with open('new2.bin', 'rb') as ifile:
    HEAPREF = np.frombuffer(ifile.read(), dtype=np.int8)

def get_diff(arr1, arr2):
    diff_indices = np.where(arr1 != arr2)[0]

    gap_size = 1  # You can adjust this value based on the gap tolerance you want

    if diff_indices.size > 0:
        # Find continuous segments allowing for a gap of `gap_size`
        continuous_segments = np.split(diff_indices, np.where(np.diff(diff_indices) > gap_size)[0] + 1)
    else:
        return []

    out = []
    last = None
    for x in continuous_segments:
        if last is None:
            last= x
            continue
        
        if last[-1] + 2 == x[0]:
            last = np.concatenate((last, x))
        elif x[0] - last[-1] > 4:
            lref = []
            lx = last[-1]
            match = True
            while lx < x[0]:
                lx+=2
                if arr1[lx] == 0 and arr2[lx] == 0:
                    lref.append(lx)
                else:
                    match = False
                    break
            if match:
                last = np.concatenate((last, np.array(lref), x))
            else:
                out.append(bytes(arr2[last]).replace(b'\x00', b''))
                last= x
        else:
            last = x

    return out

def logwrap(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        args_flatten_txt = '()'
        if args:
            args_flatten = [f'(index == {args[0]})'] + [f'(a{idx} == {arg})' for idx, arg in enumerate(args[1:], start=1)]
            args_flatten_txt = ' && '.join(args_flatten)
        log_msg = f"'{func.__name__}' {args_flatten_txt}"
            
        if self.func_stack:
            for k, v in self.func_stack.items():
                log_wasm(k ,v)
            
            self.func_stack = {}


        if self.START_DEBUG:
            logging.info(log_msg)

        if self.START_DEBUG:
            if func.__name__ == 'log':
                if args == ( 61160,):
                    logging.info("found log 61160," + log_msg)
                    with open('predebug.bin', 'wb') as ifile:
                        ifile.write(bytes(self.HEAP8))
                    # 1/0
        try:
            ret =  func(self, *args, **kwargs)
        except Exception as e:
            logging.error(f"'{func.__name__} {args}' failed")
            logging.error(f"'{func.__name__}' failed", exc_info=True)
            raise e
        
        if self.START_DEBUG:
            if self.HEAP32[276996112//4] == 1651450491:
                print("object found")
                with open('after3.bin', 'wb') as ifile:
                    ifile.write(bytes(self.HEAP8))
                
                1/0

        # if self.START_DEBUG:
        #     arrdiff = get_diff(HEAPREF, self.HEAP8)
        #     if any(b'64348649965706215a56805d' in x for x in arrdiff ):
        #         print("object found")
        #         with open('after3.bin', 'wb') as ifile:
        #             ifile.write(bytes(self.HEAP8))
        #         1/0

        return ret
    
    return wrapper

class wasm_base:
    def __init__(self):
        self.START_DEBUG=False

        self.ENV = {}
        self.GETENV_RET = {}
        self.PAGE_SIZE = 16384
        self.WASM_PAGE_SIZE = 65536
        self.ASMJS_PAGE_SIZE = 16777216
        self.MIN_TOTAL_MEMORY = 16777216
        self.TOTAL_MEMORY = 33554432
        
        self.TOTAL_STACK= 5242880
        self.STATIC_BASE = 1024
        self.STATICTOP = 5948976
        self.DYNAMICTOP_PTR = self.staticAlloc(4)
        self.staticSealed = True
        self.STACKTOP = self.STACK_BASE = self.alignMemory(self.STATICTOP)
        self.STACK_MAX = self.STACK_BASE + self.TOTAL_STACK
        self.DYNAMIC_BASE = self.alignMemory(self.STACK_MAX)
        
        self.clock_start = None
        self.SYSCALLS = JSSYS(self)
        self.init_time = time.time()*1000 #start time
        self.___buildEnvironment = False
        self.runtimeInitialized = True
        self.streams = {
            sys.stdin.fileno() : FS(sys.stdin.fileno(), 'dev/tty', tty=True),
            sys.stdout.fileno() : FS(sys.stdout.fileno(), 'dev/tty', tty=True),
            sys.stderr.fileno() : FS(sys.stderr.fileno(), 'dev/tty1', tty=True)
        }

        self.JSEVENTS = {}
        self.PTHREAD_SPECIFIC = {}
        self.PTHREAD_SPECIFIC_NEXT_KEY = 1
        with open('testing/funcidx.txt', 'r') as ofile:
            row = ofile.read()
        self.func_tables = re.findall(r'\d+', row[row.find('func'):])
        self.func_stack = {}


        self.GLctx_VERSION= 7938
        self.GLctx_SHADING_LANGUAGE_VERSION = 35724
        self.GLctx_getSupportedExtensions= ['EXT_clip_control', 'EXT_color_buffer_float', 'EXT_color_buffer_half_float', 'EXT_conservative_depth', 'EXT_depth_clamp', 'EXT_disjoint_timer_query_webgl2', 'EXT_float_blend', 'EXT_polygon_offset_clamp', 'EXT_render_snorm', 'EXT_texture_compression_bptc', 'EXT_texture_compression_rgtc', 'EXT_texture_filter_anisotropic', 'EXT_texture_mirror_clamp_to_edge', 'EXT_texture_norm16', 'KHR_parallel_shader_compile', 'NV_shader_noperspective_interpolation', 'OES_draw_buffers_indexed', 'OES_sample_variables', 'OES_shader_multisample_interpolation', 'OES_texture_float_linear', 'OVR_multiview2', 'WEBGL_blend_func_extended', 'WEBGL_clip_cull_distance', 'WEBGL_compressed_texture_s3tc', 'WEBGL_compressed_texture_s3tc_srgb', 'WEBGL_debug_renderer_info', 'WEBGL_debug_shaders', 'WEBGL_lose_context', 'WEBGL_multi_draw', 'WEBGL_polygon_mode', 'WEBGL_provoking_vertex', 'WEBGL_stencil_texturing']

        self.ALLOC_NORMAL = 0
        self.ALLOC_STACK = 1
        self.ALLOC_STATIC = 2
        self.ALLOC_NONE = 4

        self.canvas = CANVAS()
        self.GL = GL()

        self.EXCEPTIONS_infos ={}
        self.EXCEPTIONS_caught = []

        self._cxa_find_matching_catch_buffer = None
        self.tm_current = 5948912
        self._tzset_called =False

        self.Module_no_exit_runtime= True
        self.func_wrappers = {}                                                                 
        self.threads ={}
        # t = threading.Timer(1, self.custom_thread )
        # t.start()
        self.ws = WebSocketClientManager(self)
        self.main_loop_tid =None

        self.videoInstances  = {}
        
        # Create a session object
        self.rpcs = {}

    def staticAlloc(self, size):
        ret = self.STATICTOP
        self.STATICTOP = self.STATICTOP + size + 15 & -16
        return ret
    
    def alignMemory(self, size, factor=16):
        ret = size = math.ceil(size / factor) * factor;
        return ret
        
    @logwrap
    def log(self, *args):
        return
    
    @logwrap
    def log2(self, *args):
        return

    @property
    def import_object(self):
        return {
            "abort": Func(self.store, FuncType([ValType.i32()], []), self.abort),
            "enlargeMemory": Func(self.store, FuncType([], [ValType.i32()]), self.enlargeMemory),
            "getTotalMemory": Func(self.store, FuncType([], [ValType.i32()]), self.getTotalMemory),
            "abortOnCannotGrowMemory": Func(self.store, FuncType([], [ValType.i32()]), self.abortOnCannotGrowMemory),
            "invoke_dddi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.i32()], [ValType.f64()]), self.invoke_dddi),
            "invoke_dii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_dii),
            "invoke_diii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_diii),
            "invoke_diiid": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64()], [ValType.f64()]), self.invoke_diiid),
            "invoke_diiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_diiii),
            "invoke_ffffi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32()], [ValType.f64()]), self.invoke_ffffi),
            "invoke_fffi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.i32()], [ValType.f64()]), self.invoke_fffi),
            "invoke_fi": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fi),
            "invoke_fii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fii),
            "invoke_fiifi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], [ValType.f64()]), self.invoke_fiifi),
            "invoke_fiifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fiifii),
            "invoke_fiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fiii),
            "invoke_fiiif": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64()], [ValType.f64()]), self.invoke_fiiif),
            "invoke_fiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fiiii),
            "invoke_i": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self.invoke_i),
            "invoke_ifi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.i32()], [ValType.i32()]), self.invoke_ifi),
            "invoke_ii": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_ii),
            "invoke_iifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iifii),
            "invoke_iii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iii),
            "invoke_iiifi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], [ValType.i32()]), self.invoke_iiifi),
            "invoke_iiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiii),
            "invoke_iiiifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiifii),
            "invoke_iiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiii),
            "invoke_iiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiii),
            "invoke_iiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiii),
            "invoke_iiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiiii),
            "invoke_iiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiiiii),
            "invoke_iiiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiiiiii),
            "invoke_iiiiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiiiiiii),
            "invoke_v": Func(self.store, FuncType([ValType.i32()], []), self.invoke_v),
            "invoke_vi": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self.invoke_vi),
            "invoke_vidiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_vidiii),
            "invoke_vifffi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32()], []), self.invoke_vifffi),
            "invoke_vifi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), self.invoke_vifi),
            "invoke_vifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_vifii),
            "invoke_vii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_vii),
            "invoke_viidi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), self.invoke_viidi),
            "invoke_viidii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viidii),
            "invoke_viiff": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64()], []), self.invoke_viiff),
            "invoke_viiffi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.i32()], []), self.invoke_viiffi),
            "invoke_viifi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), self.invoke_viifi),
            "invoke_viifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viifii),
            "invoke_viii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viii),
            "invoke_viiif": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64()], []), self.invoke_viiif),
            "invoke_viiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiii),
            "invoke_viiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiii),
            "invoke_viiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiii),
            "invoke_viiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiii),
            "invoke_viiiiiiifddfii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiifddfii),
            "invoke_viiiiiiiffffii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiiffffii),
            "invoke_viiiiiiifiifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiifiifii),
            "invoke_viiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiii),
            "invoke_viiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiiii),
            "invoke_viiiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiiiii),
            "_ES_AddEventHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._ES_AddEventHandler),
            "_ES_Close": Func(self.store, FuncType([ValType.i32()], []), self._ES_Close),
            "_ES_Create": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._ES_Create),
            "_ES_IsSupported": Func(self.store, FuncType([], [ValType.i32()]), self._ES_IsSupported),
            "_ES_Release": Func(self.store, FuncType([ValType.i32()], []), self._ES_Release),
            "_GetInputFieldSelectionEnd": Func(self.store, FuncType([], [ValType.i32()]), self._GetInputFieldSelectionEnd),
            "_GetInputFieldSelectionStart": Func(self.store, FuncType([], [ValType.i32()]), self._GetInputFieldSelectionStart),
            "_GetInputFieldValue": Func(self.store, FuncType([], [ValType.i32()]), self._GetInputFieldValue),
            "_HideInputField": Func(self.store, FuncType([], []), self._HideInputField),
            "_IsInputFieldActive": Func(self.store, FuncType([], [ValType.i32()]), self._IsInputFieldActive),
            "_JS_Cursor_SetImage": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Cursor_SetImage),
            "_JS_Cursor_SetShow": Func(self.store, FuncType([ValType.i32()], []), self._JS_Cursor_SetShow),
            "_JS_Eval_ClearInterval": Func(self.store, FuncType([ValType.i32()], []), self._JS_Eval_ClearInterval),
            "_JS_Eval_OpenURL": Func(self.store, FuncType([ValType.i32()], []), self._JS_Eval_OpenURL),
            "_JS_Eval_SetInterval": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Eval_SetInterval),
            "_JS_FileSystem_Initialize": Func(self.store, FuncType([], []), self._JS_FileSystem_Initialize),
            "_JS_FileSystem_Sync": Func(self.store, FuncType([], []), self._JS_FileSystem_Sync),
            "_JS_Log_Dump": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Log_Dump),
            "_JS_Log_StackTrace": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Log_StackTrace),
            "_JS_Sound_Create_Channel": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Sound_Create_Channel),
            "_JS_Sound_GetLength": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Sound_GetLength),
            "_JS_Sound_GetLoadState": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Sound_GetLoadState),
            "_JS_Sound_Init": Func(self.store, FuncType([], []), self._JS_Sound_Init),
            "_JS_Sound_Load": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Sound_Load),
            "_JS_Sound_Load_PCM": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Sound_Load_PCM),
            "_JS_Sound_Play": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64()], []), self._JS_Sound_Play),
            "_JS_Sound_ReleaseInstance": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Sound_ReleaseInstance),
            "_JS_Sound_ResumeIfNeeded": Func(self.store, FuncType([], []), self._JS_Sound_ResumeIfNeeded),
            "_JS_Sound_Set3D": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Sound_Set3D),
            "_JS_Sound_SetListenerOrientation": Func(self.store, FuncType([ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64()], []), self._JS_Sound_SetListenerOrientation),
            "_JS_Sound_SetListenerPosition": Func(self.store, FuncType([ValType.f64(),ValType.f64(),ValType.f64()], []), self._JS_Sound_SetListenerPosition),
            "_JS_Sound_SetLoop": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Sound_SetLoop),
            "_JS_Sound_SetLoopPoints": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64()], []), self._JS_Sound_SetLoopPoints),
            "_JS_Sound_SetPaused": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Sound_SetPaused),
            "_JS_Sound_SetPitch": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Sound_SetPitch),
            "_JS_Sound_SetPosition": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64()], []), self._JS_Sound_SetPosition),
            "_JS_Sound_SetVolume": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Sound_SetVolume),
            "_JS_Sound_Stop": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Sound_Stop),
            "_JS_SystemInfo_GetBrowserName": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetBrowserName),
            "_JS_SystemInfo_GetBrowserVersionString": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetBrowserVersionString),
            "_JS_SystemInfo_GetCanvasClientSize": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_SystemInfo_GetCanvasClientSize),
            "_JS_SystemInfo_GetDocumentURL": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetDocumentURL),
            "_JS_SystemInfo_GetGPUInfo": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetGPUInfo),
            "_JS_SystemInfo_GetLanguage": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetLanguage),
            "_JS_SystemInfo_GetMemory": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_GetMemory),
            "_JS_SystemInfo_GetOS": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetOS),
            "_JS_SystemInfo_GetPreferredDevicePixelRatio": Func(self.store, FuncType([], [ValType.f64()]), self._JS_SystemInfo_GetPreferredDevicePixelRatio),
            "_JS_SystemInfo_GetScreenSize": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_SystemInfo_GetScreenSize),
            "_JS_SystemInfo_GetStreamingAssetsURL": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetStreamingAssetsURL),
            "_JS_SystemInfo_HasCursorLock": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_HasCursorLock),
            "_JS_SystemInfo_HasFullscreen": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_HasFullscreen),
            "_JS_SystemInfo_HasWebGL": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_HasWebGL),
            "_JS_SystemInfo_IsMobile": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_IsMobile),
            "_JS_Video_CanPlayFormat": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_CanPlayFormat),
            "_JS_Video_Create": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_Create),
            "_JS_Video_Destroy": Func(self.store, FuncType([ValType.i32()], []), self._JS_Video_Destroy),
            "_JS_Video_Duration": Func(self.store, FuncType([ValType.i32()], [ValType.f64()]), self._JS_Video_Duration),
            "_JS_Video_EnableAudioTrack": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_EnableAudioTrack),
            "_JS_Video_GetAudioLanguageCode": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Video_GetAudioLanguageCode),
            "_JS_Video_GetNumAudioTracks": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_GetNumAudioTracks),
            "_JS_Video_Height": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_Height),
            "_JS_Video_IsPlaying": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_IsPlaying),
            "_JS_Video_IsReady": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_IsReady),
            "_JS_Video_Pause": Func(self.store, FuncType([ValType.i32()], []), self._JS_Video_Pause),
            "_JS_Video_Play": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Video_Play),
            "_JS_Video_Seek": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Video_Seek),
            "_JS_Video_SetEndedHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_SetEndedHandler),
            "_JS_Video_SetErrorHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_SetErrorHandler),
            "_JS_Video_SetLoop": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Video_SetLoop),
            "_JS_Video_SetMute": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Video_SetMute),
            "_JS_Video_SetPlaybackRate": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Video_SetPlaybackRate),
            "_JS_Video_SetReadyHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_SetReadyHandler),
            "_JS_Video_SetSeekedOnceHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_SetSeekedOnceHandler),
            "_JS_Video_SetVolume": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Video_SetVolume),
            "_JS_Video_Time": Func(self.store, FuncType([ValType.i32()], [ValType.f64()]), self._JS_Video_Time),
            "_JS_Video_UpdateToTexture": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Video_UpdateToTexture),
            "_JS_Video_Width": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_Width),
            "_JS_WebCamVideo_CanPlay": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_WebCamVideo_CanPlay),
            "_JS_WebCamVideo_GetDeviceName": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_WebCamVideo_GetDeviceName),
            "_JS_WebCamVideo_GetNativeHeight": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_WebCamVideo_GetNativeHeight),
            "_JS_WebCamVideo_GetNativeWidth": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_WebCamVideo_GetNativeWidth),
            "_JS_WebCamVideo_GetNumDevices": Func(self.store, FuncType([], [ValType.i32()]), self._JS_WebCamVideo_GetNumDevices),
            "_JS_WebCamVideo_GrabFrame": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebCamVideo_GrabFrame),
            "_JS_WebCamVideo_Start": Func(self.store, FuncType([ValType.i32()], []), self._JS_WebCamVideo_Start),
            "_JS_WebCamVideo_Stop": Func(self.store, FuncType([ValType.i32()], []), self._JS_WebCamVideo_Stop),
            "_JS_WebCam_IsSupported": Func(self.store, FuncType([], [ValType.i32()]), self._JS_WebCam_IsSupported),
            "_JS_WebRequest_Abort": Func(self.store, FuncType([ValType.i32()], []), self._JS_WebRequest_Abort),
            "_JS_WebRequest_Create": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_WebRequest_Create),
            "_JS_WebRequest_GetResponseHeaders": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_WebRequest_GetResponseHeaders),
            "_JS_WebRequest_Release": Func(self.store, FuncType([ValType.i32()], []), self._JS_WebRequest_Release),
            "_JS_WebRequest_Send": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebRequest_Send),
            "_JS_WebRequest_SetProgressHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebRequest_SetProgressHandler),
            "_JS_WebRequest_SetRequestHeader": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebRequest_SetRequestHeader),
            "_JS_WebRequest_SetResponseHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebRequest_SetResponseHandler),
            "_JS_WebRequest_SetTimeout": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_WebRequest_SetTimeout),
            "_NativeCall": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._NativeCall),
            "_SetInputFieldSelection": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._SetInputFieldSelection),
            "_ShowInputField": Func(self.store, FuncType([ValType.i32()], []), self._ShowInputField),
            "_WS_Close": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._WS_Close),
            "_WS_Create": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._WS_Create),
            "_WS_GetBufferedAmount": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._WS_GetBufferedAmount),
            "_WS_GetState": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._WS_GetState),
            "_WS_Release": Func(self.store, FuncType([ValType.i32()], []), self._WS_Release),
            "_WS_Send_Binary": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._WS_Send_Binary),
            "_WS_Send_String": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._WS_Send_String),
            "_XHR_Abort": Func(self.store, FuncType([ValType.i32()], []), self._XHR_Abort),
            "_XHR_Create": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._XHR_Create),
            "_XHR_GetResponseHeaders": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._XHR_GetResponseHeaders),
            "_XHR_GetStatusLine": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._XHR_GetStatusLine),
            "_XHR_Release": Func(self.store, FuncType([ValType.i32()], []), self._XHR_Release),
            "_XHR_Send": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._XHR_Send),
            "_XHR_SetLoglevel": Func(self.store, FuncType([ValType.i32()], []), self._XHR_SetLoglevel),
            "_XHR_SetProgressHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._XHR_SetProgressHandler),
            "_XHR_SetRequestHeader": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._XHR_SetRequestHeader),
            "_XHR_SetResponseHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._XHR_SetResponseHandler),
            "_XHR_SetTimeout": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._XHR_SetTimeout),
            "___buildEnvironment": Func(self.store, FuncType([ValType.i32()], []), self._buildEnvironment),
            "___cxa_allocate_exception": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._cxa_allocate_exception),
            "___cxa_begin_catch": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._cxa_begin_catch),
            "___cxa_end_catch": Func(self.store, FuncType([], []), self._cxa_end_catch),
            "___cxa_find_matching_catch_2": Func(self.store, FuncType([], [ValType.i32()]), self._cxa_find_matching_catch_2),
            "___cxa_find_matching_catch_3": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._cxa_find_matching_catch_3),
            "___cxa_find_matching_catch_4": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._cxa_find_matching_catch_4),
            "___cxa_free_exception": Func(self.store, FuncType([ValType.i32()], []), self._cxa_free_exception),
            "___cxa_pure_virtual": Func(self.store, FuncType([], []), self._cxa_pure_virtual),
            "___cxa_rethrow": Func(self.store, FuncType([], []), self._cxa_rethrow),
            "___cxa_throw": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._cxa_throw),
            "___lock": Func(self.store, FuncType([ValType.i32()], []), self._lock),
            "___map_file": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._map_file),
            "___resumeException": Func(self.store, FuncType([ValType.i32()], []), self._resumeException),
            "___setErrNo": Func(self.store, FuncType([ValType.i32()], []), self._setErrNo),
            "___syscall10": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall10),
            "___syscall102": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall102),
            "___syscall122": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall122),
            "___syscall140": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall140),
            "___syscall142": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall142),
            "___syscall145": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall145),
            "___syscall146": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall146),
            "___syscall15": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall15),
            "___syscall168": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall168),
            "___syscall183": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall183),
            "___syscall192": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall192),
            "___syscall193": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall193),
            "___syscall194": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall194),
            "___syscall195": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall195),
            "___syscall196": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall196),
            "___syscall197": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall197),
            "___syscall199": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall199),
            "___syscall220": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall220),
            "___syscall221": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall221),
            "___syscall268": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall268),
            "___syscall3": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall3),
            "___syscall33": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall33),
            "___syscall38": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall38),
            "___syscall39": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall39),
            "___syscall4": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall4),
            "___syscall40": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall40),
            "___syscall42": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall42),
            "___syscall5": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall5),
            "___syscall54": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall54),
            "___syscall6": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall6),
            "___syscall63": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall63),
            "___syscall77": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall77),
            "___syscall85": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall85),
            "___syscall91": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall91),
            "___unlock": Func(self.store, FuncType([ValType.i32()], []), self._unlock),
            "_abort": Func(self.store, FuncType([], []), self._abort),
            "_atexit": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._atexit),
            "_clock": Func(self.store, FuncType([], [ValType.i32()]), self._clock),
            "_clock_getres": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._clock_getres),
            "_clock_gettime": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._clock_gettime),
            "_difftime": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.f64()]), self._difftime),
            "_dlclose": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._dlclose),
            "_dlopen": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._dlopen),
            "_dlsym": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._dlsym),
            "_emscripten_asm_const_i": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_asm_const_i),
            "_emscripten_asm_const_sync_on_main_thread_i": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_asm_const_sync_on_main_thread_i),
            "_emscripten_cancel_main_loop": Func(self.store, FuncType([], []), self._emscripten_cancel_main_loop),
            "_emscripten_exit_fullscreen": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_exit_fullscreen),
            "_emscripten_exit_pointerlock": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_exit_pointerlock),
            "_emscripten_get_canvas_element_size": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_get_canvas_element_size),
            "_emscripten_get_fullscreen_status": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_get_fullscreen_status),
            "_emscripten_get_gamepad_status": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_get_gamepad_status),
            "_emscripten_get_main_loop_timing": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._emscripten_get_main_loop_timing),
            "_emscripten_get_now": Func(self.store, FuncType([], [ValType.f64()]), self._emscripten_get_now),
            "_emscripten_get_num_gamepads": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_get_num_gamepads),
            "_emscripten_has_threading_support": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_has_threading_support),
            "_emscripten_html5_remove_all_event_listeners": Func(self.store, FuncType([], []), self._emscripten_html5_remove_all_event_listeners),
            "_emscripten_is_webgl_context_lost": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_is_webgl_context_lost),
            "_emscripten_log": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._emscripten_log),
            "_emscripten_longjmp": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._emscripten_longjmp),
            "_emscripten_memcpy_big": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_memcpy_big),
            "_emscripten_num_logical_cores": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_num_logical_cores),
            "_emscripten_request_fullscreen": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_request_fullscreen),
            "_emscripten_request_pointerlock": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_request_pointerlock),
            "_emscripten_set_blur_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_blur_callback_on_thread),
            "_emscripten_set_canvas_element_size": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_canvas_element_size),
            "_emscripten_set_dblclick_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_dblclick_callback_on_thread),
            "_emscripten_set_devicemotion_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_devicemotion_callback_on_thread),
            "_emscripten_set_deviceorientation_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_deviceorientation_callback_on_thread),
            "_emscripten_set_focus_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_focus_callback_on_thread),
            "_emscripten_set_fullscreenchange_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_fullscreenchange_callback_on_thread),
            "_emscripten_set_gamepadconnected_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_gamepadconnected_callback_on_thread),
            "_emscripten_set_gamepaddisconnected_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_gamepaddisconnected_callback_on_thread),
            "_emscripten_set_keydown_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_keydown_callback_on_thread),
            "_emscripten_set_keypress_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_keypress_callback_on_thread),
            "_emscripten_set_keyup_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_keyup_callback_on_thread),
            "_emscripten_set_main_loop": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._emscripten_set_main_loop),
            "_emscripten_set_main_loop_timing": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_main_loop_timing),
            "_emscripten_set_mousedown_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_mousedown_callback_on_thread),
            "_emscripten_set_mousemove_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_mousemove_callback_on_thread),
            "_emscripten_set_mouseup_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_mouseup_callback_on_thread),
            "_emscripten_set_touchcancel_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_touchcancel_callback_on_thread),
            "_emscripten_set_touchend_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_touchend_callback_on_thread),
            "_emscripten_set_touchmove_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_touchmove_callback_on_thread),
            "_emscripten_set_touchstart_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_touchstart_callback_on_thread),
            "_emscripten_set_wheel_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_wheel_callback_on_thread),
            "_emscripten_webgl_create_context": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_webgl_create_context),
            "_emscripten_webgl_destroy_context": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_webgl_destroy_context),
            "_emscripten_webgl_enable_extension": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_webgl_enable_extension),
            "_emscripten_webgl_get_current_context": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_webgl_get_current_context),
            "_emscripten_webgl_init_context_attributes": Func(self.store, FuncType([ValType.i32()], []), self._emscripten_webgl_init_context_attributes),
            "_emscripten_webgl_make_context_current": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_webgl_make_context_current),
            "_exit": Func(self.store, FuncType([ValType.i32()], []), self._exit),
            "_flock": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._flock),
            "_getaddrinfo": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._getaddrinfo),
            "_getenv": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._getenv),
            "_gethostbyaddr": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._gethostbyaddr),
            "_gethostbyname": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._gethostbyname),
            "_getnameinfo": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._getnameinfo),
            "_getpagesize": Func(self.store, FuncType([], [ValType.i32()]), self._getpagesize),
            "_getpwuid": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._getpwuid),
            "_gettimeofday": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._gettimeofday),
            "_glActiveTexture": Func(self.store, FuncType([ValType.i32()], []), self._glActiveTexture),
            "_glAttachShader": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glAttachShader),
            "_glBeginQuery": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBeginQuery),
            "_glBeginTransformFeedback": Func(self.store, FuncType([ValType.i32()], []), self._glBeginTransformFeedback),
            "_glBindAttribLocation": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBindAttribLocation),
            "_glBindBuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindBuffer),
            "_glBindBufferBase": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBindBufferBase),
            "_glBindBufferRange": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBindBufferRange),
            "_glBindFramebuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindFramebuffer),
            "_glBindRenderbuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindRenderbuffer),
            "_glBindSampler": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindSampler),
            "_glBindTexture": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindTexture),
            "_glBindTransformFeedback": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindTransformFeedback),
            "_glBindVertexArray": Func(self.store, FuncType([ValType.i32()], []), self._glBindVertexArray),
            "_glBlendEquation": Func(self.store, FuncType([ValType.i32()], []), self._glBlendEquation),
            "_glBlendEquationSeparate": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBlendEquationSeparate),
            "_glBlendFuncSeparate": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBlendFuncSeparate),
            "_glBlitFramebuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBlitFramebuffer),
            "_glBufferData": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBufferData),
            "_glBufferSubData": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBufferSubData),
            "_glCheckFramebufferStatus": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glCheckFramebufferStatus),
            "_glClear": Func(self.store, FuncType([ValType.i32()], []), self._glClear),
            "_glClearBufferfi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), self._glClearBufferfi),
            "_glClearBufferfv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glClearBufferfv),
            "_glClearBufferuiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glClearBufferuiv),
            "_glClearColor": Func(self.store, FuncType([ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64()], []), self._glClearColor),
            "_glClearDepthf": Func(self.store, FuncType([ValType.f64()], []), self._glClearDepthf),
            "_glClearStencil": Func(self.store, FuncType([ValType.i32()], []), self._glClearStencil),
            "_glColorMask": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glColorMask),
            "_glCompileShader": Func(self.store, FuncType([ValType.i32()], []), self._glCompileShader),
            "_glCompressedTexImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCompressedTexImage2D),
            "_glCompressedTexSubImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCompressedTexSubImage2D),
            "_glCompressedTexSubImage3D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCompressedTexSubImage3D),
            "_glCopyBufferSubData": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCopyBufferSubData),
            "_glCopyTexImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCopyTexImage2D),
            "_glCopyTexSubImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCopyTexSubImage2D),
            "_glCreateProgram": Func(self.store, FuncType([], [ValType.i32()]), self._glCreateProgram),
            "_glCreateShader": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glCreateShader),
            "_glCullFace": Func(self.store, FuncType([ValType.i32()], []), self._glCullFace),
            "_glDeleteBuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteBuffers),
            "_glDeleteFramebuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteFramebuffers),
            "_glDeleteProgram": Func(self.store, FuncType([ValType.i32()], []), self._glDeleteProgram),
            "_glDeleteQueries": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteQueries),
            "_glDeleteRenderbuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteRenderbuffers),
            "_glDeleteSamplers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteSamplers),
            "_glDeleteShader": Func(self.store, FuncType([ValType.i32()], []), self._glDeleteShader),
            "_glDeleteSync": Func(self.store, FuncType([ValType.i32()], []), self._glDeleteSync),
            "_glDeleteTextures": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteTextures),
            "_glDeleteTransformFeedbacks": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteTransformFeedbacks),
            "_glDeleteVertexArrays": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteVertexArrays),
            "_glDepthFunc": Func(self.store, FuncType([ValType.i32()], []), self._glDepthFunc),
            "_glDepthMask": Func(self.store, FuncType([ValType.i32()], []), self._glDepthMask),
            "_glDetachShader": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDetachShader),
            "_glDisable": Func(self.store, FuncType([ValType.i32()], []), self._glDisable),
            "_glDisableVertexAttribArray": Func(self.store, FuncType([ValType.i32()], []), self._glDisableVertexAttribArray),
            "_glDrawArrays": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glDrawArrays),
            "_glDrawArraysInstanced": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glDrawArraysInstanced),
            "_glDrawBuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDrawBuffers),
            "_glDrawElements": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glDrawElements),
            "_glDrawElementsInstanced": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glDrawElementsInstanced),
            "_glEnable": Func(self.store, FuncType([ValType.i32()], []), self._glEnable),
            "_glEnableVertexAttribArray": Func(self.store, FuncType([ValType.i32()], []), self._glEnableVertexAttribArray),
            "_glEndQuery": Func(self.store, FuncType([ValType.i32()], []), self._glEndQuery),
            "_glEndTransformFeedback": Func(self.store, FuncType([], []), self._glEndTransformFeedback),
            "_glFenceSync": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glFenceSync),
            "_glFinish": Func(self.store, FuncType([], []), self._glFinish),
            "_glFlush": Func(self.store, FuncType([], []), self._glFlush),
            "_glFlushMappedBufferRange": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glFlushMappedBufferRange),
            "_glFramebufferRenderbuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glFramebufferRenderbuffer),
            "_glFramebufferTexture2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glFramebufferTexture2D),
            "_glFramebufferTextureLayer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glFramebufferTextureLayer),
            "_glFrontFace": Func(self.store, FuncType([ValType.i32()], []), self._glFrontFace),
            "_glGenBuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenBuffers),
            "_glGenFramebuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenFramebuffers),
            "_glGenQueries": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenQueries),
            "_glGenRenderbuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenRenderbuffers),
            "_glGenSamplers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenSamplers),
            "_glGenTextures": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenTextures),
            "_glGenTransformFeedbacks": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenTransformFeedbacks),
            "_glGenVertexArrays": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenVertexArrays),
            "_glGenerateMipmap": Func(self.store, FuncType([ValType.i32()], []), self._glGenerateMipmap),
            "_glGetActiveAttrib": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveAttrib),
            "_glGetActiveUniform": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveUniform),
            "_glGetActiveUniformBlockName": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveUniformBlockName),
            "_glGetActiveUniformBlockiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveUniformBlockiv),
            "_glGetActiveUniformsiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveUniformsiv),
            "_glGetAttribLocation": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glGetAttribLocation),
            "_glGetError": Func(self.store, FuncType([], [ValType.i32()]), self._glGetError),
            "_glGetFramebufferAttachmentParameteriv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetFramebufferAttachmentParameteriv),
            "_glGetIntegeri_v": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetIntegeri_v),
            "_glGetIntegerv": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGetIntegerv),
            "_glGetInternalformativ": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetInternalformativ),
            "_glGetProgramBinary": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetProgramBinary),
            "_glGetProgramInfoLog": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetProgramInfoLog),
            "_glGetProgramiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetProgramiv),
            "_glGetRenderbufferParameteriv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetRenderbufferParameteriv),
            "_glGetShaderInfoLog": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetShaderInfoLog),
            "_glGetShaderPrecisionFormat": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetShaderPrecisionFormat),
            "_glGetShaderSource": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetShaderSource),
            "_glGetShaderiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetShaderiv),
            "_glGetString": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glGetString),
            "_glGetStringi": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glGetStringi),
            "_glGetTexParameteriv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetTexParameteriv),
            "_glGetUniformBlockIndex": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glGetUniformBlockIndex),
            "_glGetUniformIndices": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetUniformIndices),
            "_glGetUniformLocation": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glGetUniformLocation),
            "_glGetUniformiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetUniformiv),
            "_glGetVertexAttribiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetVertexAttribiv),
            "_glInvalidateFramebuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glInvalidateFramebuffer),
            "_glIsEnabled": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glIsEnabled),
            "_glIsVertexArray": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glIsVertexArray),
            "_glLinkProgram": Func(self.store, FuncType([ValType.i32()], []), self._glLinkProgram),
            "_glMapBufferRange": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._glMapBufferRange),
            "_glPixelStorei": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glPixelStorei),
            "_glPolygonOffset": Func(self.store, FuncType([ValType.f64(),ValType.f64()], []), self._glPolygonOffset),
            "_glProgramBinary": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glProgramBinary),
            "_glProgramParameteri": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glProgramParameteri),
            "_glReadBuffer": Func(self.store, FuncType([ValType.i32()], []), self._glReadBuffer),
            "_glReadPixels": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glReadPixels),
            "_glRenderbufferStorage": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glRenderbufferStorage),
            "_glRenderbufferStorageMultisample": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glRenderbufferStorageMultisample),
            "_glSamplerParameteri": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glSamplerParameteri),
            "_glScissor": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glScissor),
            "_glShaderSource": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glShaderSource),
            "_glStencilFuncSeparate": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glStencilFuncSeparate),
            "_glStencilMask": Func(self.store, FuncType([ValType.i32()], []), self._glStencilMask),
            "_glStencilOpSeparate": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glStencilOpSeparate),
            "_glTexImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexImage2D),
            "_glTexImage3D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexImage3D),
            "_glTexParameterf": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64()], []), self._glTexParameterf),
            "_glTexParameteri": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexParameteri),
            "_glTexParameteriv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexParameteriv),
            "_glTexStorage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexStorage2D),
            "_glTexStorage3D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexStorage3D),
            "_glTexSubImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexSubImage2D),
            "_glTexSubImage3D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexSubImage3D),
            "_glTransformFeedbackVaryings": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTransformFeedbackVaryings),
            "_glUniform1fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform1fv),
            "_glUniform1i": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glUniform1i),
            "_glUniform1iv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform1iv),
            "_glUniform1uiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform1uiv),
            "_glUniform2fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform2fv),
            "_glUniform2iv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform2iv),
            "_glUniform2uiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform2uiv),
            "_glUniform3fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform3fv),
            "_glUniform3iv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform3iv),
            "_glUniform3uiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform3uiv),
            "_glUniform4fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform4fv),
            "_glUniform4iv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform4iv),
            "_glUniform4uiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform4uiv),
            "_glUniformBlockBinding": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniformBlockBinding),
            "_glUniformMatrix3fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniformMatrix3fv),
            "_glUniformMatrix4fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniformMatrix4fv),
            "_glUnmapBuffer": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glUnmapBuffer),
            "_glUseProgram": Func(self.store, FuncType([ValType.i32()], []), self._glUseProgram),
            "_glValidateProgram": Func(self.store, FuncType([ValType.i32()], []), self._glValidateProgram),
            "_glVertexAttrib4f": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64()], []), self._glVertexAttrib4f),
            "_glVertexAttrib4fv": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glVertexAttrib4fv),
            "_glVertexAttribIPointer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glVertexAttribIPointer),
            "_glVertexAttribPointer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glVertexAttribPointer),
            "_glViewport": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glViewport),
            "_gmtime": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._gmtime),
            "_inet_addr": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._inet_addr),
            "_llvm_eh_typeid_for": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._llvm_eh_typeid_for),
            "_llvm_exp2_f32": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_exp2_f32),
            "_llvm_log10_f32": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_log10_f32),
            "_llvm_log10_f64": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_log10_f64),
            "_llvm_log2_f32": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_log2_f32),
            "_llvm_trap": Func(self.store, FuncType([], []), self._llvm_trap),
            "_llvm_trunc_f32": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_trunc_f32),
            "_localtime": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._localtime),
            "_longjmp": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._longjmp),
            "_mktime": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._mktime),
            "_pthread_cond_destroy": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_cond_destroy),
            "_pthread_cond_init": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_cond_init),
            "_pthread_cond_timedwait": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_cond_timedwait),
            "_pthread_cond_wait": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_cond_wait),
            "_pthread_getspecific": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_getspecific),
            "_pthread_key_create": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_key_create),
            "_pthread_key_delete": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_key_delete),
            "_pthread_mutex_destroy": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_mutex_destroy),
            "_pthread_mutex_init": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_mutex_init),
            "_pthread_mutexattr_destroy": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_mutexattr_destroy),
            "_pthread_mutexattr_init": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_mutexattr_init),
            "_pthread_mutexattr_setprotocol": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_mutexattr_setprotocol),
            "_pthread_mutexattr_settype": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_mutexattr_settype),
            "_pthread_once": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_once),
            "_pthread_setspecific": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_setspecific),
            "_sched_yield": Func(self.store, FuncType([], [ValType.i32()]), self._sched_yield),
            "_setenv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._setenv),
            "_sigaction": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._sigaction),
            "_sigemptyset": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._sigemptyset),
            "_strftime": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._strftime),
            "_sysconf": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._sysconf),
            "_time": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._time),
            "_unsetenv": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._unsetenv),
            "_utime": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._utime),
            "f64-rem": Func(self.store, FuncType([ValType.f64(),ValType.f64()], [ValType.f64()]), self.f64_rem),
            "invoke_iiiiij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiij),
            "invoke_iiiijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiijii),
            "invoke_iiiijjii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiijjii),
            "invoke_iiiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiji),
            "invoke_iiijiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiijiii),
            "invoke_iij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iij),
            "invoke_iiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiji),
            "invoke_iijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iijii),
            "invoke_ijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_ijii),
            "invoke_j": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self.invoke_j),
            "invoke_jdi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.i32()], [ValType.i32()]), self.invoke_jdi),
            "invoke_ji": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_ji),
            "invoke_jii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jii),
            "invoke_jiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiii),
            "invoke_jiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiii),
            "invoke_jiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiiii),
            "invoke_jiiiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiiiiiiiii),
            "invoke_jiiij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiij),
            "invoke_jiiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiji),
            "invoke_jiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiji),
            "invoke_jijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jijii),
            "invoke_jijiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jijiii),
            "invoke_jijj": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jijj),
            "invoke_jji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jji),
            "invoke_viiiiiiifjjfii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiifjjfii),
            "invoke_viiiijiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiijiiii),
            "invoke_viiij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiij),
            "invoke_viiiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiji),
            "invoke_viij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viij),
            "invoke_viiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiji),
            "invoke_viijji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viijji),
            "invoke_viji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viji),
            "invoke_vijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_vijii),
            "___atomic_fetch_add_8": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._atomic_fetch_add_8),
            "_glClientWaitSync": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._glClientWaitSync),

            "log": Func(self.store, FuncType([ValType.i32()], []), self.log),
            "log2": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self.log2),
            }

    @logwrap
    def abort(self, *args):
        logging.error("abort not implemented")
        return 

    @logwrap
    def enlargeMemory(self):
        PAGE_MULTIPLE = self.WASM_PAGE_SIZE
        LIMIT = 2147483648 - PAGE_MULTIPLE
        if self.HEAP32[self.DYNAMICTOP_PTR >> 2] > LIMIT:
            return False
        OLD_TOTAL_MEMORY = self.TOTAL_MEMORY
        self.TOTAL_MEMORY = max(self.TOTAL_MEMORY, self.MIN_TOTAL_MEMORY)
        while self.TOTAL_MEMORY < self.HEAP32[self.DYNAMICTOP_PTR >> 2]:
            if self.TOTAL_MEMORY <= 536870912:
                self.TOTAL_MEMORY = self.alignUp(2 * self.TOTAL_MEMORY, PAGE_MULTIPLE)
            else:
                self.TOTAL_MEMORY = min(self.alignUp((3 * self.TOTAL_MEMORY + 2147483648) // 4, PAGE_MULTIPLE), LIMIT)

        replacement = self.reallocBuffer(self.TOTAL_MEMORY)
        if (not replacement or self.HEAP8.nbytes != self.TOTAL_MEMORY):
            self.TOTAL_MEMORY = OLD_TOTAL_MEMORY
            return False
        
        return True

    @logwrap
    def getTotalMemory(self):
        return self.TOTAL_MEMORY
    

    @logwrap
    def abortOnCannotGrowMemory(self, *args):
        logging.error("abortOnCannotGrowMemory not implemented")
        return 0

    @logwrap
    def invoke_dddi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_dddi(*args)
        except:
            logging.error('invoke_dddi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_dii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_dii(*args)
        except:
            logging.error('invoke_dii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_diii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_diii(*args)
        except:
            logging.error('invoke_diii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_diiid(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_diiid(*args)
        except:
            logging.error('invoke_diiid fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_diiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_diiii(*args)
        except:
            logging.error('invoke_diiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_ffffi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_ffffi(*args)
        except:
            logging.error('invoke_ffffi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_fffi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_fffi(*args)
        except:
            logging.error('invoke_fffi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_fi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_fi(*args)
        except:
            logging.error('invoke_fi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_fii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_fii(*args)
        except:
            logging.error('invoke_fii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_fiifi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_fiifi(*args)
        except:
            logging.error('invoke_fiifi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_fiifii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_fiifii(*args)
        except:
            logging.error('invoke_fiifii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_fiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_fiii(*args)
        except:
            logging.error('invoke_fiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_fiiif(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_fiiif(*args)
        except:
            logging.error('invoke_fiiif fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_fiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_fiiii(*args)
        except:
            logging.error('invoke_fiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_i(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_i(*args)
        except:
            logging.error('invoke_i fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_ifi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_ifi(*args)
        except:
            logging.error('invoke_ifi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_ii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_ii(*args)
        except:
            logging.error('invoke_ii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iifii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iifii(*args)
        except:
            logging.error('invoke_iifii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iii(*args)
        except:
            logging.error('invoke_iii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiifi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiifi(*args)
        except:
            logging.error('invoke_iiifi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiii(*args)
        except:
            logging.error('invoke_iiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiifii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiifii(*args)
        except:
            logging.error('invoke_iiiifii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiii(*args)
        except:
            logging.error('invoke_iiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiii(*args)
        except:
            logging.error('invoke_iiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiiii(*args)
        except:
            logging.error('invoke_iiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiiiii(*args)
        except:
            logging.error('invoke_iiiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiiiiii(*args)
        except:
            logging.error('invoke_iiiiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiiiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiiiiiii(*args)
        except:
            logging.error('invoke_iiiiiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiiiiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiiiiiiii(*args)
        except:
            logging.error('invoke_iiiiiiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_v(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_v(*args)
        except:
            logging.error('invoke_v fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_vi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_vi(*args)
        except:
            logging.error('invoke_vi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_vidiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_vidiii(*args)
        except:
            logging.error('invoke_vidiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_vifffi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_vifffi(*args)
        except:
            logging.error('invoke_vifffi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_vifi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_vifi(*args)
        except:
            logging.error('invoke_vifi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_vifii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_vifii(*args)
        except:
            logging.error('invoke_vifii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_vii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_vii(*args)
        except:
            logging.error('invoke_vii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viidi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viidi(*args)
        except:
            logging.error('invoke_viidi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viidii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viidii(*args)
        except:
            logging.error('invoke_viidii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiff(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiff(*args)
        except:
            logging.error('invoke_viiff fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiffi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiffi(*args)
        except:
            logging.error('invoke_viiffi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viifi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viifi(*args)
        except:
            logging.error('invoke_viifi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viifii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viifii(*args)
        except:
            logging.error('invoke_viifii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viii(*args)
        except:
            logging.error('invoke_viii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiif(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiif(*args)
        except:
            logging.error('invoke_viiif fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiii(*args)
        except:
            logging.error('invoke_viiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiii(*args)
        except:
            logging.error('invoke_viiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiiii(*args)
        except:
            logging.error('invoke_viiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiiiii(*args)
        except:
            logging.error('invoke_viiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiiiiifddfii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiiiiifddfii(*args)
        except:
            logging.error('invoke_viiiiiiifddfii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiiiiiffffii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiiiiiffffii(*args)
        except:
            logging.error('invoke_viiiiiiiffffii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiiiiifiifii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiiiiifiifii(*args)
        except:
            logging.error('invoke_viiiiiiifiifii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiiiiii(*args)
        except:
            logging.error('invoke_viiiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiiiiiii(*args)
        except:
            logging.error('invoke_viiiiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiiiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiiiiiiii(*args)
        except:
            logging.error('invoke_viiiiiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def _ES_AddEventHandler(self, *args):
        logging.error("_ES_AddEventHandler not implemented")
        return 

    @logwrap
    def _ES_Close(self, *args):
        logging.error("_ES_Close not implemented")
        return 

    @logwrap
    def _ES_Create(self, *args):
        logging.error("_ES_Create not implemented")
        return 0

    @logwrap
    def _ES_IsSupported(self, *args):
        logging.error("_ES_IsSupported not implemented")
        return 0

    @logwrap
    def _ES_Release(self, *args):
        logging.error("_ES_Release not implemented")
        return 

    @logwrap
    def _GetInputFieldSelectionEnd(self, *args):
        logging.error("_GetInputFieldSelectionEnd not implemented")
        return 0

    @logwrap
    def _GetInputFieldSelectionStart(self, *args):
        logging.error("_GetInputFieldSelectionStart not implemented")
        return 0

    @logwrap
    def _GetInputFieldValue(self, *args):
        logging.error("_GetInputFieldValue not implemented")
        return 0

    @logwrap
    def _HideInputField(self, *args):
        logging.error("_HideInputField not implemented")
        return 

    @logwrap
    def _IsInputFieldActive(self, *args):
        logging.error("_IsInputFieldActive not implemented")
        return 0

    @logwrap
    def _JS_Cursor_SetImage(self, *args):
        logging.error("_JS_Cursor_SetImage not implemented")
        return 

    @logwrap
    def _JS_Cursor_SetShow(self, *args):
        logging.error("_JS_Cursor_SetShow not implemented")
        return 

    @logwrap
    def _JS_Eval_ClearInterval(self, *args):
        logging.error("_JS_Eval_ClearInterval not implemented")
        return 

    @logwrap
    def _JS_Eval_OpenURL(self, *args):
        logging.error("_JS_Eval_OpenURL not implemented")
        return 

    @logwrap
    def _JS_Eval_SetInterval(self, *args):
        logging.error("_JS_Eval_SetInterval not implemented")
        return 0

    @logwrap
    def _JS_FileSystem_Initialize(self, *args):
        logging.error("_JS_FileSystem_Initialize not implemented")
        return 

    @logwrap
    def _JS_FileSystem_Sync(self):
        logging.warning("_JS_FileSystem_Sync -- ignored")
        return 
    
    @logwrap
    def _JS_Log_Dump(self,ptr,param1):
        strr = self.Pointer_stringify(ptr);
        if param1 in [0, 1, 4]:
            logging.error(strr)
        elif param1 == 2:
            logging.warning(strr)
        elif param1 in [3, 5]:
            logging.info(strr)
        else:
            logging.error("Unknown console message param1!")
            logging.error(strr)
        return
    

    @logwrap
    def _JS_Log_StackTrace(self, *args):
        logging.error("_JS_Log_StackTrace not implemented")
        return 

    @logwrap
    def _JS_Sound_Create_Channel(self, *args):
        logging.error("_JS_Sound_Create_Channel not implemented")
        return 0

    @logwrap
    def _JS_Sound_GetLength(self, *args):
        logging.error("_JS_Sound_GetLength not implemented")
        return 0

    @logwrap
    def _JS_Sound_GetLoadState(self, *args):
        logging.error("_JS_Sound_GetLoadState not implemented")
        return 0

    @logwrap
    def _JS_Sound_Init(self, *args):
        logging.error("_JS_Sound_Init not implemented")
        return 

    @logwrap
    def _JS_Sound_Load(self, *args):
        logging.error("_JS_Sound_Load not implemented")
        return 0

    @logwrap
    def _JS_Sound_Load_PCM(self, *args):
        logging.error("_JS_Sound_Load_PCM not implemented")
        return 0

    @logwrap
    def _JS_Sound_Play(self, *args):
        logging.error("_JS_Sound_Play not implemented")
        return 

    @logwrap
    def _JS_Sound_ReleaseInstance(self, *args):
        logging.error("_JS_Sound_ReleaseInstance not implemented")
        return 0

    @logwrap
    def _JS_Sound_ResumeIfNeeded(self, *args):
        logging.error("_JS_Sound_ResumeIfNeeded not implemented")
        return 

    @logwrap
    def _JS_Sound_Set3D(self, *args):
        logging.error("_JS_Sound_Set3D not implemented")
        return 

    @logwrap
    def _JS_Sound_SetListenerOrientation(self, *args):
        logging.warning("_JS_Sound_SetListenerOrientation not implemented -- ignored")
        return 

    @logwrap
    def _JS_Sound_SetListenerPosition(self,param0,param1,param2):
        logging.warning("_JS_Sound_SetListenerPosition not implemented -- ignored")
        return 

    @logwrap
    def _JS_Sound_SetLoop(self,param0,param1):
        logging.error("_JS_Sound_SetLoop not implemented")
        return 
    
    @logwrap
    def _JS_Sound_SetLoopPoints(self, *args):
        logging.error("_JS_Sound_SetLoopPoints not implemented")
        return 

    @logwrap
    def _JS_Sound_SetPaused(self, *args):
        logging.error("_JS_Sound_SetPaused not implemented")
        return 

    @logwrap
    def _JS_Sound_SetPitch(self, *args):
        logging.error("_JS_Sound_SetPitch not implemented")
        return 

    @logwrap
    def _JS_Sound_SetPosition(self, *args):
        logging.error("_JS_Sound_SetPosition not implemented")
        return 

    @logwrap
    def _JS_Sound_SetVolume(self, *args):
        logging.error("_JS_Sound_SetVolume not implemented")
        return 

    @logwrap
    def _JS_Sound_Stop(self, *args):
        logging.error("_JS_Sound_Stop not implemented")
        return 

    @logwrap
    def _JS_SystemInfo_GetBrowserName(self, *args):
        logging.error("_JS_SystemInfo_GetBrowserName not implemented")
        return 0

    @logwrap
    def _JS_SystemInfo_GetBrowserVersionString(self, *args):
        logging.error("_JS_SystemInfo_GetBrowserVersionString not implemented")
        return 0

    @logwrap
    def _JS_SystemInfo_GetCanvasClientSize(self,domElementSelector, outWidth, outHeight):
        self.HEAPF64[outWidth >> 3] = 1920
        self.HEAPF64[outHeight >> 3] = 910

    @logwrap
    def _JS_SystemInfo_GetDocumentURL(self, *args):
        logging.error("_JS_SystemInfo_GetDocumentURL not implemented")
        return 0

    @logwrap
    def _JS_SystemInfo_GetGPUInfo(self, *args):
        logging.error("_JS_SystemInfo_GetGPUInfo not implemented")
        return 0

    @logwrap
    def _JS_SystemInfo_GetLanguage(self, *args):
        logging.error("_JS_SystemInfo_GetLanguage not implemented")
        return 0

    @logwrap
    def _JS_SystemInfo_GetMemory(self, *args):
        logging.error("_JS_SystemInfo_GetMemory not implemented")
        return 0

    @logwrap
    def _JS_SystemInfo_GetOS(self, *args):
        logging.error("_JS_SystemInfo_GetOS not implemented")
        return 0

    @logwrap
    def _JS_SystemInfo_GetPreferredDevicePixelRatio(self, *args):
        return 1.0

    @logwrap
    def _JS_SystemInfo_GetScreenSize(self,param0,param1):
        self.HEAPF64[param0 >> 3] = 1920
        self.HEAPF64[param1 >> 3] = 1080

    @logwrap
    def _JS_SystemInfo_GetStreamingAssetsURL(self, *args):
        logging.error("_JS_SystemInfo_GetStreamingAssetsURL not implemented")
        return 0

    @logwrap
    def _JS_SystemInfo_HasCursorLock(self):
        logging.error("_JS_SystemInfo_HasCursorLock not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_HasFullscreen(self):
        logging.error("_JS_SystemInfo_HasFullscreen not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_HasWebGL(self):
        return 2
    
    @logwrap
    def _JS_SystemInfo_IsMobile(self):
        logging.error("_JS_SystemInfo_IsMobile not implemented")
        return 0
    
    @logwrap
    def _JS_Video_CanPlayFormat(self,param0):
        format = self.UTF8ToString(param0)
        return 1

    @logwrap
    def _JS_Video_Create(self,param0):
        url = self.UTF8ToString(param0)
        self.videoInstances[len(self.videoInstances)+1] = {'url': url, 'state': 0}
        return len(self.videoInstances)
    
    @logwrap
    def _JS_Video_Destroy(self,param0):
        logging.error("_JS_Video_Destroy not implemented")
        return 
    
    @logwrap
    def _JS_Video_Duration(self,param0):
        logging.error("_JS_Video_Duration not implemented")
        return 0

    @logwrap
    def _JS_Video_EnableAudioTrack(self,param0,param1,param2):
        return 
    
    @logwrap
    def _JS_Video_GetAudioLanguageCode(self,param0,param1):
        logging.error("_JS_Video_GetAudioLanguageCode not implemented")
        return 0
    
    @logwrap
    def _JS_Video_GetNumAudioTracks(self,param0):
        logging.warning("_JS_Video_GetNumAudioTracks -- ignored")
        return 1

    @logwrap
    def _JS_Video_Height(self,param0):
        return 1080
    
    @logwrap
    def _JS_Video_IsPlaying(self,param0):
        logging.warning("_JS_Video_IsPlaying -- ignored")
        return 0

    @logwrap
    def _JS_Video_IsReady(self,param0):
        v = self.videoInstances[param0]
        state= v['state']
        v['state'] =1
        return state

    @logwrap
    def _JS_Video_Pause(self,param0):
        logging.error("_JS_Video_Pause not implemented")
        return 
    
    @logwrap
    def _JS_Video_Play(self,param0,param1):
        return 

    @logwrap
    def _JS_Video_Seek(self,param0,param1):
        logging.error("_JS_Video_Seek not implemented")
        return 
    
    @logwrap
    def _JS_Video_SetEndedHandler(self,video, ref, onended):
        self.videoInstances[video]['onendedCallback'] = onended
        self.videoInstances[video]['onendedRef'] = ref
        return 
    
    @logwrap
    def _JS_Video_SetErrorHandler(self,param0,param1,param2):
        logging.warning("_JS_Video_SetErrorHandler -- ignored")
        return 

    @logwrap
    def _JS_Video_SetLoop(self, *args):
        logging.error("_JS_Video_SetLoop not implemented")
        return 

    @logwrap
    def _JS_Video_SetMute(self, *args):
        logging.error("_JS_Video_SetMute not implemented")
        return 

    @logwrap
    def _JS_Video_SetPlaybackRate(self, *args):
        logging.error("_JS_Video_SetPlaybackRate not implemented")
        return 

    @logwrap
    def _JS_Video_SetReadyHandler(self, *args):
        logging.error("_JS_Video_SetReadyHandler not implemented")
        return 

    @logwrap
    def _JS_Video_SetSeekedOnceHandler(self, *args):
        logging.error("_JS_Video_SetSeekedOnceHandler not implemented")
        return 

    @logwrap
    def _JS_Video_SetVolume(self, *args):
        logging.error("_JS_Video_SetVolume not implemented")
        return 

    @logwrap
    def _JS_Video_Time(self, *args):
        logging.error("_JS_Video_Time not implemented")
        return 0

    @logwrap
    def _JS_Video_UpdateToTexture(self, *args):
        logging.error("_JS_Video_UpdateToTexture not implemented")
        return 0

    @logwrap
    def _JS_Video_Width(self, *args):
        logging.error("_JS_Video_Width not implemented")
        return 0

    @logwrap
    def _JS_WebCamVideo_CanPlay(self, *args):
        logging.error("_JS_WebCamVideo_CanPlay not implemented")
        return 0

    @logwrap
    def _JS_WebCamVideo_GetDeviceName(self, *args):
        logging.error("_JS_WebCamVideo_GetDeviceName not implemented")
        return 0

    @logwrap
    def _JS_WebCamVideo_GetNativeHeight(self, *args):
        logging.error("_JS_WebCamVideo_GetNativeHeight not implemented")
        return 0

    @logwrap
    def _JS_WebCamVideo_GetNativeWidth(self, *args):
        logging.error("_JS_WebCamVideo_GetNativeWidth not implemented")
        return 0

    @logwrap
    def _JS_WebCamVideo_GetNumDevices(self, *args):
        logging.error("_JS_WebCamVideo_GetNumDevices not implemented")
        return 0

    @logwrap
    def _JS_WebCamVideo_GrabFrame(self, *args):
        logging.error("_JS_WebCamVideo_GrabFrame not implemented")
        return 

    @logwrap
    def _JS_WebCamVideo_Start(self, *args):
        logging.error("_JS_WebCamVideo_Start not implemented")
        return 

    @logwrap
    def _JS_WebCamVideo_Stop(self, *args):
        logging.error("_JS_WebCamVideo_Stop not implemented")
        return 

    @logwrap
    def _JS_WebCam_IsSupported(self, *args):
        logging.error("_JS_WebCam_IsSupported not implemented")
        return 0

    @logwrap
    def _JS_WebRequest_Abort(self, *args):
        logging.error("_JS_WebRequest_Abort not implemented")
        return 

    @logwrap
    def _JS_WebRequest_Create(self, *args):
        logging.error("_JS_WebRequest_Create not implemented")
        return 0

    @logwrap
    def _JS_WebRequest_GetResponseHeaders(self, *args):
        logging.error("_JS_WebRequest_GetResponseHeaders not implemented")
        return 0

    @logwrap
    def _JS_WebRequest_Release(self, *args):
        logging.error("_JS_WebRequest_Release not implemented")
        return 

    @logwrap
    def _JS_WebRequest_Send(self, *args):
        logging.error("_JS_WebRequest_Send not implemented")
        return 

    @logwrap
    def _JS_WebRequest_SetProgressHandler(self, *args):
        logging.error("_JS_WebRequest_SetProgressHandler not implemented")
        return 

    @logwrap
    def _JS_WebRequest_SetRequestHeader(self, *args):
        logging.error("_JS_WebRequest_SetRequestHeader not implemented")
        return 

    @logwrap
    def _JS_WebRequest_SetResponseHandler(self, *args):
        logging.error("_JS_WebRequest_SetResponseHandler not implemented")
        return 

    @logwrap
    def _JS_WebRequest_SetTimeout(self, *args):
        logging.error("_JS_WebRequest_SetTimeout not implemented")
        return 

    @logwrap
    def _NativeCall(self, *args):
        logging.error("_NativeCall not implemented")
        return 

    @logwrap
    def _SetInputFieldSelection(self, *args):
        logging.error("_SetInputFieldSelection not implemented")
        return 

    @logwrap
    def _ShowInputField(self, *args):
        logging.error("_ShowInputField not implemented")
        return 

    @logwrap
    def _WS_Close(self, *args):
        logging.error("_WS_Close not implemented")
        return 

    @logwrap
    def _WS_Create(self, *args):
        logging.error("_WS_Create not implemented")
        return 0

    @logwrap
    def _WS_GetBufferedAmount(self, *args):
        logging.error("_WS_GetBufferedAmount not implemented")
        return 0

    @logwrap
    def _WS_GetState(self, *args):
        logging.error("_WS_GetState not implemented")
        return 0

    @logwrap
    def _WS_Release(self, *args):
        logging.error("_WS_Release not implemented")
        return 

    @logwrap
    def _WS_Send_Binary(self, *args):
        logging.error("_WS_Send_Binary not implemented")
        return 0

    @logwrap
    def _WS_Send_String(self, *args):
        logging.error("_WS_Send_String not implemented")
        return 0

    @logwrap
    def _XHR_Abort(self, *args):
        logging.error("_XHR_Abort not implemented")
        return 

    @logwrap
    def _XHR_Create(self, *args):
        logging.error("_XHR_Create not implemented")
        return 0

    @logwrap
    def _XHR_GetResponseHeaders(self, *args):
        logging.error("_XHR_GetResponseHeaders not implemented")
        return 

    @logwrap
    def _XHR_GetStatusLine(self, *args):
        logging.error("_XHR_GetStatusLine not implemented")
        return 

    @logwrap
    def _XHR_Release(self, *args):
        logging.error("_XHR_Release not implemented")
        return 

    @logwrap
    def _XHR_Send(self, *args):
        logging.error("_XHR_Send not implemented")
        return 

    @logwrap
    def _XHR_SetLoglevel(self, *args):
        logging.error("_XHR_SetLoglevel not implemented")
        return 

    @logwrap
    def _XHR_SetProgressHandler(self, *args):
        logging.error("_XHR_SetProgressHandler not implemented")
        return 

    @logwrap
    def _XHR_SetRequestHeader(self, *args):
        logging.error("_XHR_SetRequestHeader not implemented")
        return 

    @logwrap
    def _XHR_SetResponseHandler(self, *args):
        logging.error("_XHR_SetResponseHandler not implemented")
        return 

    @logwrap
    def _XHR_SetTimeout(self, *args):
        logging.error("_XHR_SetTimeout not implemented")
        return 

    @logwrap
    def _buildEnvironment(self, *args):
        logging.error("_buildEnvironment not implemented")
        return 

    @logwrap
    def _cxa_allocate_exception(self, *args):
        logging.error("_cxa_allocate_exception not implemented")
        return 0

    @logwrap
    def _cxa_begin_catch(self, *args):
        logging.error("_cxa_begin_catch not implemented")
        return 0

    @logwrap
    def _cxa_end_catch(self, *args):
        logging.error("_cxa_end_catch not implemented")
        return 

    @logwrap
    def _cxa_find_matching_catch_2(self, *args):
        logging.error("_cxa_find_matching_catch_2 not implemented")
        return 0

    @logwrap
    def _cxa_find_matching_catch_3(self, *args):
        logging.error("_cxa_find_matching_catch_3 not implemented")
        return 0

    @logwrap
    def _cxa_find_matching_catch_4(self, *args):
        logging.error("_cxa_find_matching_catch_4 not implemented")
        return 0

    @logwrap
    def _cxa_free_exception(self, *args):
        logging.error("_cxa_free_exception not implemented")
        return 

    @logwrap
    def _cxa_pure_virtual(self, *args):
        logging.error("_cxa_pure_virtual not implemented")
        return 

    @logwrap
    def _cxa_rethrow(self, *args):
        logging.error("_cxa_rethrow not implemented")
        return 

    @logwrap
    def _cxa_throw(self, *args):
        logging.error("_cxa_throw not implemented")
        return 

    @logwrap
    def _lock(self, *args):
        logging.error("_lock not implemented")
        return 

    @logwrap
    def _map_file(self, *args):
        logging.error("_map_file not implemented")
        return 0

    @logwrap
    def _resumeException(self, *args):
        logging.error("_resumeException not implemented")
        return 

    @logwrap
    def _setErrNo(self, *args):
        logging.error("_setErrNo not implemented")
        return 

    @logwrap
    def _syscall10(self, *args):
        logging.error("_syscall10 not implemented")
        return 0

    @logwrap
    def _syscall102(self, *args):
        logging.error("_syscall102 not implemented")
        return 0

    @logwrap
    def _syscall122(self, *args):
        logging.error("_syscall122 not implemented")
        return 0

    @logwrap
    def _syscall140(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            offset_high = self.SYSCALLS.get()
            offset_low = self.SYSCALLS.get()
            result = self.SYSCALLS.get()
            whence = self.SYSCALLS.get()
            offset = offset_low
            os.lseek(stream.fileno(), offset, whence)
            self.HEAP32[result >> 2] =  stream.tell()
            return 0

        except Exception as e:
            logging.error("_syscall140" , exc_info=True)
            return -1
        
    @logwrap
    def _syscall142(self, *args):
        logging.error("_syscall142 not implemented")
        return 0

    @logwrap
    def _syscall145(self, *args):
        logging.error("_syscall145 not implemented")
        return 0

    @logwrap
    def _syscall146(self, *args):
        logging.error("_syscall146 not implemented")
        return 0

    @logwrap
    def _syscall15(self, *args):
        logging.error("_syscall15 not implemented")
        return 0

    @logwrap
    def _syscall168(self, *args):
        logging.error("_syscall168 not implemented")
        return 0

    @logwrap
    def _syscall183(self, *args):
        logging.error("_syscall183 not implemented")
        return 0

    @logwrap
    def _syscall192(self, *args):
        logging.error("_syscall192 not implemented")
        return 0

    @logwrap
    def _syscall193(self, *args):
        logging.error("_syscall193 not implemented")
        return 0

    @logwrap
    def _syscall194(self, *args):
        logging.error("_syscall194 not implemented")
        return 0

    @logwrap
    def _syscall195(self, *args):
        logging.error("_syscall195 not implemented")
        return 0

    @logwrap
    def _syscall196(self, *args):
        logging.error("_syscall196 not implemented")
        return 0

    @logwrap
    def _syscall197(self, *args):
        logging.error("_syscall197 not implemented")
        return 0

    @logwrap
    def _syscall199(self, *args):
        logging.error("_syscall199 not implemented")
        return 0

    @logwrap
    def _syscall220(self, *args):
        logging.error("_syscall220 not implemented")
        return 0

    @logwrap
    def _syscall221(self, *args):
        logging.error("_syscall221 not implemented")
        return 0

    @logwrap
    def _syscall268(self, *args):
        logging.error("_syscall268 not implemented")
        return 0

    @logwrap
    def _syscall3(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            buf = self.SYSCALLS.get()
            count = self.SYSCALLS.get()
            ret = stream.read_to_buffer(self.HEAP8, buf, count)
            return ret
        except Exception as e:
            logging.error("_syscall3 failed" , exc_info=True)
            return -1
    

    @logwrap
    def _syscall33(self, *args):
        logging.error("_syscall33 not implemented")
        return 0

    @logwrap
    def _syscall38(self, *args):
        logging.error("_syscall38 not implemented")
        return 0

    @logwrap
    def _syscall39(self, *args):
        logging.error("_syscall39 not implemented")
        return 0

    @logwrap
    def _syscall4(self, notinuse, varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            buf = self.SYSCALLS.get()
            count = self.SYSCALLS.get()
            ret = stream.write_contents(self.HEAP8, buf, count)
            return ret
        except Exception as e:
            logging.error("_syscall4 failed" , exc_info=True)
            return -1
        
    @logwrap
    def _syscall40(self, *args):
        logging.error("_syscall40 not implemented")
        return 0

    @logwrap
    def _syscall42(self, *args):
        logging.error("_syscall42 not implemented")
        return 0

    @logwrap
    def _syscall5(self,param0,varargs):

        self.SYSCALLS.varargs = varargs
        try:
            pathname = self.SYSCALLS.getStr()
            flags = self.SYSCALLS.get()
            mode = self.SYSCALLS.get()
            logging.info(f'{pathname}, {flags} ,{mode}')

            if not (flags & 64):
                mode = 0

            if not os.path.exists(pathname):
                if mode ==0:
                    return -2
                else:
                    # create regular file
                    os.makedirs('/'.join(pathname.split('/')[:-1]), exist_ok=True)
                    with open(pathname, 'w') as ofile:
                        pass

            logging.info(f'{pathname}, {flags} ,{mode}')
            fd= os.open(pathname, flags=flags, mode=mode)
            self.streams[fd] =  FS(fd, pathname)
            return fd
        except Exception as e:
            logging.error("_syscall5" , exc_info=True)
            return -1
        
    @logwrap
    def _syscall54(self, *args):
        logging.error("_syscall54 not implemented")
        return 0

    @logwrap
    def _syscall6(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            fd = stream.fileno()
            stream.close()
            self.streams.pop(fd)
            return 0    
        except Exception as e:
            logging.error("_syscall6" , exc_info=True)
            return -1
    

    @logwrap
    def _syscall63(self, *args):
        logging.error("_syscall63 not implemented")
        return 0

    @logwrap
    def _syscall77(self, *args):
        logging.error("_syscall77 not implemented")
        return 0

    @logwrap
    def _syscall85(self, *args):
        logging.error("_syscall85 not implemented")
        return 0

    @logwrap
    def _syscall91(self, *args):
        logging.error("_syscall91 not implemented")
        return 0

    @logwrap
    def _unlock(self, *args):
        logging.error("_unlock not implemented")
        return 

    @logwrap
    def _abort(self, *args):
        logging.error("_abort not implemented")
        return 

    @logwrap
    def _atexit(self, *args):
        logging.error("_atexit not implemented")
        return 0

    @logwrap
    def _clock(self, *args):
        logging.error("_clock not implemented")
        return 0

    @logwrap
    def _clock_getres(self, *args):
        logging.error("_clock_getres not implemented")
        return 0

    @logwrap
    def _clock_gettime(self, *args):
        logging.error("_clock_gettime not implemented")
        return 0

    @logwrap
    def _difftime(self, *args):
        logging.error("_difftime not implemented")
        return 0

    @logwrap
    def _dlclose(self, *args):
        logging.error("_dlclose not implemented")
        return 0

    @logwrap
    def _dlopen(self, *args):
        logging.error("_dlopen not implemented")
        return 0

    @logwrap
    def _dlsym(self, *args):
        logging.error("_dlsym not implemented")
        return 0

    @logwrap
    def _emscripten_asm_const_i(self, *args):
        # logging.error("_emscripten_asm_const_i not implemented")
        if args[0] ==2:
            return False
        return 0

    @logwrap
    def _emscripten_asm_const_sync_on_main_thread_i(self, *args):
        logging.error("_emscripten_asm_const_sync_on_main_thread_i not implemented")
        return 0

    @logwrap
    def _emscripten_cancel_main_loop(self, *args):
        logging.error("_emscripten_cancel_main_loop not implemented")
        return 

    @logwrap
    def _emscripten_exit_fullscreen(self, *args):
        logging.error("_emscripten_exit_fullscreen not implemented")
        return 0

    @logwrap
    def _emscripten_exit_pointerlock(self, *args):
        logging.error("_emscripten_exit_pointerlock not implemented")
        return 0

    @logwrap
    def _emscripten_get_canvas_element_size(self,target, width, height):
        canvas = self.canvas
        if canvas.canvasSharedPtr:
            w = self.HEAP32[canvas.canvasSharedPtr >> 2]
            h = self.HEAP32[canvas.canvasSharedPtr + 4 >> 2]
            self.HEAP32[width >> 2] = w
            self.HEAP32[height >> 2] = h
        elif canvas.offscreenCanvas:
            self.HEAP32[width >> 2] = canvas.offscreenCanvas.width
            self.HEAP32[height >> 2] = canvas.offscreenCanvas.height
        elif not canvas.controlTransferredOffscreen:
            self.HEAP32[width >> 2] = canvas.width
            self.HEAP32[height >> 2] = canvas.height
        else:
            return -4
        return 0
    
    @logwrap
    def _emscripten_get_fullscreen_status(self,eventStruct):
        self.HEAP32[eventStruct >> 2] = 0;
        self.HEAP32[eventStruct + 4 >> 2] = 1
        self.HEAP32[eventStruct + 264 >> 2] = 0
        self.HEAP32[eventStruct + 268 >> 2] = 0
        self.HEAP32[eventStruct + 272 >> 2] = 1920
        self.HEAP32[eventStruct + 276 >> 2] = 1080
        return 0

    
    @logwrap
    def _emscripten_get_gamepad_status(self,param0,param1):
        logging.warning("_emscripten_get_gamepad_status -- warning")
        return -7
    
    
    @logwrap
    def _emscripten_get_main_loop_timing(self,mode,val):
        if mode:
            self.HEAP32[mode >> 2] = 1
        if val:
            self.HEAP32[val >> 2] = 1
    

    @logwrap
    def _emscripten_get_now(self, *args):
        logging.warning("modified for decryption testing")
        # return datetime.datetime(2025,5,25, 19,17,11).timestamp()*1000 - datetime.datetime(2025,5,25, 19,17,10, 50).timestamp()*1000 
        return self.HEAPF64[5073440//8] + 1300
        return time.time()*1000 - self.init_time
    

    @logwrap
    def _emscripten_get_num_gamepads(self):
        return 4
    
    @logwrap
    def _emscripten_has_threading_support(self):
        logging.error("_emscripten_has_threading_support not implemented")
        return 0
    
    @logwrap
    def _emscripten_html5_remove_all_event_listeners(self):
        logging.error("_emscripten_html5_remove_all_event_listeners not implemented")
        return 
    
    @logwrap
    def _emscripten_is_webgl_context_lost(self,param0):
        return 0

    @logwrap
    def _emscripten_log(self, *args):
        logging.error("_emscripten_log not implemented")
        return 

    @logwrap
    def _emscripten_longjmp(self, *args):
        logging.error("_emscripten_longjmp not implemented")
        return 

    @logwrap
    def _emscripten_memcpy_big(self,dest, src, num):
        self.HEAPU8[dest:dest+num] = self.HEAPU8[src:src+num]
        return dest

    @logwrap
    def _emscripten_num_logical_cores(self, *args):
        logging.error("_emscripten_num_logical_cores not implemented")
        return 0

    @logwrap
    def _emscripten_request_fullscreen(self, *args):
        logging.error("_emscripten_request_fullscreen not implemented")
        return 0

    @logwrap
    def _emscripten_request_pointerlock(self, *args):
        logging.error("_emscripten_request_pointerlock not implemented")
        return 0

    @logwrap
    def _emscripten_set_blur_callback_on_thread(self, *args):
        logging.error("_emscripten_set_blur_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_canvas_element_size(self, *args):
        return 0

    @logwrap
    def _emscripten_set_dblclick_callback_on_thread(self, *args):
        logging.error("_emscripten_set_dblclick_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_devicemotion_callback_on_thread(self, *args):
        logging.error("_emscripten_set_devicemotion_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_deviceorientation_callback_on_thread(self, *args):
        logging.error("_emscripten_set_deviceorientation_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_focus_callback_on_thread(self, *args):
        logging.error("_emscripten_set_focus_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_fullscreenchange_callback_on_thread(self, *args):
        logging.error("_emscripten_set_fullscreenchange_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_gamepadconnected_callback_on_thread(self, *args):
        logging.error("_emscripten_set_gamepadconnected_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_gamepaddisconnected_callback_on_thread(self, *args):
        logging.error("_emscripten_set_gamepaddisconnected_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_keydown_callback_on_thread(self, *args):
        logging.error("_emscripten_set_keydown_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_keypress_callback_on_thread(self, *args):
        logging.error("_emscripten_set_keypress_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_keyup_callback_on_thread(self, *args):
        logging.error("_emscripten_set_keyup_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_main_loop(self, *args):
        logging.error("_emscripten_set_main_loop not implemented")
        return 

    @logwrap
    def _emscripten_set_main_loop_timing(self, *args):
        logging.error("_emscripten_set_main_loop_timing not implemented")
        return 0

    @logwrap
    def _emscripten_set_mousedown_callback_on_thread(self, *args):
        logging.error("_emscripten_set_mousedown_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_mousemove_callback_on_thread(self, *args):
        logging.error("_emscripten_set_mousemove_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_mouseup_callback_on_thread(self, *args):
        logging.error("_emscripten_set_mouseup_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_touchcancel_callback_on_thread(self, *args):
        logging.error("_emscripten_set_touchcancel_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_touchend_callback_on_thread(self, *args):
        logging.error("_emscripten_set_touchend_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_touchmove_callback_on_thread(self, *args):
        logging.error("_emscripten_set_touchmove_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_touchstart_callback_on_thread(self, *args):
        logging.error("_emscripten_set_touchstart_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_set_wheel_callback_on_thread(self, *args):
        logging.error("_emscripten_set_wheel_callback_on_thread not implemented")
        return 0

    @logwrap
    def _emscripten_webgl_create_context(self, *args):
        logging.error("_emscripten_webgl_create_context not implemented")
        return 0

    @logwrap
    def _emscripten_webgl_destroy_context(self, *args):
        logging.error("_emscripten_webgl_destroy_context not implemented")
        return 0

    @logwrap
    def _emscripten_webgl_enable_extension(self, *args):
        logging.error("_emscripten_webgl_enable_extension not implemented")
        return 0

    @logwrap
    def _emscripten_webgl_get_current_context(self, *args):
        logging.error("_emscripten_webgl_get_current_context not implemented")
        return 0

    @logwrap
    def _emscripten_webgl_init_context_attributes(self, *args):
        logging.error("_emscripten_webgl_init_context_attributes not implemented")
        return 

    @logwrap
    def _emscripten_webgl_make_context_current(self, *args):
        logging.error("_emscripten_webgl_make_context_current not implemented")
        return 0

    @logwrap
    def _exit(self, *args):
        logging.error("_exit not implemented")
        return 

    @logwrap
    def _flock(self, *args):
        logging.error("_flock not implemented")
        return 0

    @logwrap
    def _getaddrinfo(self, *args):
        logging.error("_getaddrinfo not implemented")
        return 0

    @logwrap
    def _getenv(self, *args):
        logging.error("_getenv not implemented")
        return 0

    @logwrap
    def _gethostbyaddr(self, *args):
        logging.error("_gethostbyaddr not implemented")
        return 0

    @logwrap
    def _gethostbyname(self, *args):
        logging.error("_gethostbyname not implemented")
        return 0

    @logwrap
    def _getnameinfo(self, *args):
        logging.error("_getnameinfo not implemented")
        return 0

    @logwrap
    def _getpagesize(self, *args):
        logging.error("_getpagesize not implemented")
        return 0

    @logwrap
    def _getpwuid(self, *args):
        logging.error("_getpwuid not implemented")
        return 0

    @logwrap
    def _gettimeofday(self,ptr,param1):
        logging.warning("modified for decryption testing")
        now = time.time()* 1e3
        now = datetime.datetime(2025,5,25, 19,17).timestamp()*1000 
        self.HEAP32[ptr >> 2] = int(now / 1e3) 
        self.HEAP32[ptr + 4 >> 2] = int(now % 1e3 * 1e3) 
        return 0

    @logwrap
    def _glActiveTexture(self, *args):
        logging.error("_glActiveTexture not implemented")
        return 

    @logwrap
    def _glAttachShader(self, *args):
        logging.error("_glAttachShader not implemented")
        return 

    @logwrap
    def _glBeginQuery(self, *args):
        logging.error("_glBeginQuery not implemented")
        return 

    @logwrap
    def _glBeginTransformFeedback(self, *args):
        logging.error("_glBeginTransformFeedback not implemented")
        return 

    @logwrap
    def _glBindAttribLocation(self, *args):
        logging.error("_glBindAttribLocation not implemented")
        return 

    @logwrap
    def _glBindBuffer(self,target,buffer):
        if (target == 35051):
            self.GLctx_currentPixelPackBufferBinding = buffer
        elif (target == 35052):
            self.GLctx_currentPixelUnpackBufferBinding = buffer

    @logwrap
    def _glBindBufferBase(self,param0,param1,param2):
        logging.warning("_glBindBufferBase -- ignored")
        return 
    
    @logwrap
    def _glBindBufferRange(self,param0,param1,param2,param3,param4):
        logging.warning("_glBindBufferRange -- ignored")
        return 
    
    @logwrap
    def _glBindFramebuffer(self,param0,param1):
        logging.warning("_glBindFramebuffer -- ignored")
        return 
    
    @logwrap
    def _glBindRenderbuffer(self,param0,param1):
        logging.warning("_glBindRenderbuffer -- ignored")
        return 
    
    @logwrap
    def _glBindSampler(self,param0,param1):
        logging.warning("_glBindSampler -- ignored")
        return 

    @logwrap
    def _glBindTexture(self,param0,param1):
        logging.warning("_glBindTexture -- ignored")
        return 
    
    @logwrap
    def _glBindTransformFeedback(self,param0,param1):
        logging.warning("_glBindTransformFeedback -- ignored")
        return 
    
    @logwrap
    def _glBindVertexArray(self,param0):
        logging.warning("_glBindVertexArray -- ignored")
        return 
    
    @logwrap
    def _glBlendEquation(self,param0):
        logging.warning("_glBlendEquation -- ignored")
        return 
    
    @logwrap
    def _glBlendEquationSeparate(self,param0,param1):
        logging.warning("_glBlendEquationSeparate -- ignored")
        return 

    @logwrap
    def _glBlendFuncSeparate(self,param0,param1,param2,param3):
        logging.warning("_glBlendFuncSeparate -- ignored")
        return 
    
    @logwrap
    def _glBlitFramebuffer(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
        logging.warning("_glBlitFramebuffer -- ignored")
        return 
    
    @logwrap
    def _glBufferData(self,param0,param1,param2,param3):
        logging.warning("_glBufferData -- ignored")
        return 
    
    @logwrap
    def _glBufferSubData(self,param0,param1,param2,param3):
        logging.warning("_glBufferSubData -- ignored")
        return 

    @logwrap
    def _glCheckFramebufferStatus(self, *args):
        logging.error("_glCheckFramebufferStatus not implemented")
        return 0

    @logwrap
    def _glClear(self, *args):
        logging.error("_glClear not implemented")
        return 

    @logwrap
    def _glClearBufferfi(self, *args):
        logging.error("_glClearBufferfi not implemented")
        return 

    @logwrap
    def _glClearBufferfv(self, *args):
        logging.error("_glClearBufferfv not implemented")
        return 

    @logwrap
    def _glClearBufferuiv(self, *args):
        logging.error("_glClearBufferuiv not implemented")
        return 

    @logwrap
    def _glClearColor(self, *args):
        logging.error("_glClearColor not implemented")
        return 

    @logwrap
    def _glClearDepthf(self, *args):
        logging.error("_glClearDepthf not implemented")
        return 

    @logwrap
    def _glClearStencil(self, *args):
        logging.error("_glClearStencil not implemented")
        return 

    @logwrap
    def _glColorMask(self, *args):
        logging.error("_glColorMask not implemented")
        return 

    @logwrap
    def _glCompileShader(self, *args):
        logging.error("_glCompileShader not implemented")
        return 

    @logwrap
    def _glCompressedTexImage2D(self, *args):
        logging.error("_glCompressedTexImage2D not implemented")
        return 

    @logwrap
    def _glCompressedTexSubImage2D(self, *args):
        logging.error("_glCompressedTexSubImage2D not implemented")
        return 

    @logwrap
    def _glCompressedTexSubImage3D(self, *args):
        logging.error("_glCompressedTexSubImage3D not implemented")
        return 

    @logwrap
    def _glCopyBufferSubData(self, *args):
        logging.error("_glCopyBufferSubData not implemented")
        return 

    @logwrap
    def _glCopyTexImage2D(self, *args):
        logging.error("_glCopyTexImage2D not implemented")
        return 

    @logwrap
    def _glCopyTexSubImage2D(self, *args):
        logging.error("_glCopyTexSubImage2D not implemented")
        return 

    @logwrap
    def _glCreateProgram(self, *args):
        logging.error("_glCreateProgram not implemented")
        return 0

    @logwrap
    def _glCreateShader(self, *args):
        logging.error("_glCreateShader not implemented")
        return 0

    @logwrap
    def _glCullFace(self, *args):
        logging.error("_glCullFace not implemented")
        return 

    @logwrap
    def _glDeleteBuffers(self, *args):
        logging.error("_glDeleteBuffers not implemented")
        return 

    @logwrap
    def _glDeleteFramebuffers(self, *args):
        logging.error("_glDeleteFramebuffers not implemented")
        return 

    @logwrap
    def _glDeleteProgram(self, *args):
        logging.error("_glDeleteProgram not implemented")
        return 

    @logwrap
    def _glDeleteQueries(self, *args):
        logging.error("_glDeleteQueries not implemented")
        return 

    @logwrap
    def _glDeleteRenderbuffers(self, *args):
        logging.error("_glDeleteRenderbuffers not implemented")
        return 

    @logwrap
    def _glDeleteSamplers(self, *args):
        logging.error("_glDeleteSamplers not implemented")
        return 

    @logwrap
    def _glDeleteShader(self, *args):
        logging.error("_glDeleteShader not implemented")
        return 

    @logwrap
    def _glDeleteSync(self, *args):
        logging.error("_glDeleteSync not implemented")
        return 

    @logwrap
    def _glDeleteTextures(self, *args):
        logging.error("_glDeleteTextures not implemented")
        return 

    @logwrap
    def _glDeleteTransformFeedbacks(self, *args):
        logging.error("_glDeleteTransformFeedbacks not implemented")
        return 

    @logwrap
    def _glDeleteVertexArrays(self, *args):
        logging.error("_glDeleteVertexArrays not implemented")
        return 

    @logwrap
    def _glDepthFunc(self, *args):
        logging.error("_glDepthFunc not implemented")
        return 

    @logwrap
    def _glDepthMask(self, *args):
        logging.error("_glDepthMask not implemented")
        return 

    @logwrap
    def _glDetachShader(self, *args):
        logging.error("_glDetachShader not implemented")
        return 

    @logwrap
    def _glDisable(self, *args):
        logging.error("_glDisable not implemented")
        return 

    @logwrap
    def _glDisableVertexAttribArray(self, *args):
        logging.error("_glDisableVertexAttribArray not implemented")
        return 

    @logwrap
    def _glDrawArrays(self, *args):
        logging.error("_glDrawArrays not implemented")
        return 

    @logwrap
    def _glDrawArraysInstanced(self, *args):
        logging.error("_glDrawArraysInstanced not implemented")
        return 

    @logwrap
    def _glDrawBuffers(self,param0,param1):
        return 
    

    @logwrap
    def _glDrawElements(self, *args):
        logging.error("_glDrawElements not implemented")
        return 

    @logwrap
    def _glDrawElementsInstanced(self, *args):
        logging.error("_glDrawElementsInstanced not implemented")
        return 

    @logwrap
    def _glEnable(self, *args):
        logging.error("_glEnable not implemented")
        return 

    @logwrap
    def _glEnableVertexAttribArray(self, *args):
        logging.error("_glEnableVertexAttribArray not implemented")
        return 

    @logwrap
    def _glEndQuery(self, *args):
        logging.error("_glEndQuery not implemented")
        return 

    @logwrap
    def _glEndTransformFeedback(self, *args):
        logging.error("_glEndTransformFeedback not implemented")
        return 

    @logwrap
    def _glFenceSync(self, *args):
        logging.error("_glFenceSync not implemented")
        return 0

    @logwrap
    def _glFinish(self, *args):
        logging.error("_glFinish not implemented")
        return 

    @logwrap
    def _glFlush(self, *args):
        logging.error("_glFlush not implemented")
        return 

    @logwrap
    def _glFlushMappedBufferRange(self, *args):
        logging.error("_glFlushMappedBufferRange not implemented")
        return 

    @logwrap
    def _glFramebufferRenderbuffer(self,param0,param1,param2,param3):
        return 

    @logwrap
    def _glFramebufferTexture2D(self,param0,param1,param2,param3,param4):
        return 

    @logwrap
    def _glFramebufferTextureLayer(self,param0,param1,param2,param3,param4):
        return 

    @logwrap
    def _glFrontFace(self, *args):
        logging.error("_glFrontFace not implemented")
        return 

    @logwrap
    def _glGenBuffers(self,n,buffers):
        for i in range(n):
            buffer=  {'arr': [], 'type': 'buffer'}
            idx = self.GL.getNewId(self.GL.buffers)
            buffer['name'] = idx
            self.GL.buffers[idx] = buffer
            self.HEAP32[(buffers + i * 4) >> 2] = idx

    @logwrap
    def _glGenFramebuffers(self,n,ids):
        for i in range(n):
            buffer=  {'arr': [], 'type': 'Framebuffer'}
            idx = self.GL.getNewId(self.GL.framebuffers)
            buffer['name'] = idx
            self.GL.framebuffers[idx] = buffer
            self.HEAP32[(ids + i * 4) >> 2] = idx

    @logwrap
    def _glGenQueries(self, *args):
        logging.error("_glGenQueries not implemented")
        return 

    @logwrap
    def _glGenRenderbuffers(self, *args):
        logging.error("_glGenRenderbuffers not implemented")
        return 

    @logwrap
    def _glGenSamplers(self, *args):
        logging.error("_glGenSamplers not implemented")
        return 

    @logwrap
    def _glGenTextures(self,n,ids):
        for i in range(n):
            buffer=  {'arr': [], 'type': 'texture'}
            idx = self.GL.getNewId(self.GL.textures)
            buffer['name'] = idx
            self.GL.textures[idx] = buffer
            self.HEAP32[(ids + i * 4) >> 2] = idx
    
    @logwrap
    def _glGenTransformFeedbacks(self,n,ids):
        for i in range(n):
            buffer=  {'arr': [], 'type': 'transformfeedback'}
            idx = self.GL.getNewId(self.GL.transformfeedbacks)
            buffer['name'] = idx
            self.GL.transformfeedbacks[idx] = buffer
            self.HEAP32[(ids + i * 4) >> 2] = idx
    
    @logwrap
    def _glGenVertexArrays(self,n,ids):
        for i in range(n):
            buffer=  {'arr': [], 'type': 'vao'}
            idx = self.GL.getNewId(self.GL.vaos)
            buffer['name'] = idx
            self.GL.vaos[idx] = buffer
            self.HEAP32[(ids + i * 4) >> 2] = idx

    @logwrap
    def _glGenerateMipmap(self,param0):
        return 
    
    @logwrap
    def _glGetActiveAttrib(self,param0,param1,param2,param3,param4,param5,param6):
        logging.error("_glGetActiveAttrib not implemented")
        return 

    @logwrap
    def _glGetActiveUniform(self,program, index, bufSize, length, size, _type, name):
        program = self.GL.programs[program]
        if not program:
            return
        
        info = self.GL.ctx_getActiveUniform(program, index)
        if not info:
            return
        
        if bufSize > 0 and name:
            # Assuming 'name' is a byte buffer, so we use slicing
            numBytesWrittenExclNull = self.stringToUTF8(info['name'], name, bufSize)
            if length:
                self.HEAP32[length >> 2] = numBytesWrittenExclNull
        else:
            if length:
                self.HEAP32[length >> 2] = 0
        
        if size:
            self.HEAP32[size >> 2] = info['size']
        
        if _type:
            self.HEAP32[_type >> 2] = info['type']

    @logwrap
    def _glGetActiveUniformBlockName(self, *args):
        logging.error("_glGetActiveUniformBlockName not implemented")
        return 

    @logwrap
    def _glGetActiveUniformBlockiv(self, *args):
        logging.error("_glGetActiveUniformBlockiv not implemented")
        return 

    @logwrap
    def _glGetActiveUniformsiv(self, *args):
        logging.error("_glGetActiveUniformsiv not implemented")
        return 

    @logwrap
    def _glGetAttribLocation(self, *args):
        logging.error("_glGetAttribLocation not implemented")
        return 0

    @logwrap
    def _glGetError(self, *args):
        logging.error("_glGetError not implemented")
        return 0

    @logwrap
    def _glGetFramebufferAttachmentParameteriv(self, *args):
        logging.error("_glGetFramebufferAttachmentParameteriv not implemented")
        return 

    @logwrap
    def _glGetIntegeri_v(self, *args):
        logging.error("_glGetIntegeri_v not implemented")
        return 

    @logwrap
    def _glGetIntegerv(self, *args):
        logging.error("_glGetIntegerv not implemented")
        return 

    @logwrap
    def _glGetInternalformativ(self, *args):
        logging.error("_glGetInternalformativ not implemented")
        return 

    @logwrap
    def _glGetProgramBinary(self, *args):
        logging.error("_glGetProgramBinary not implemented")
        return 

    @logwrap
    def _glGetProgramInfoLog(self, *args):
        logging.error("_glGetProgramInfoLog not implemented")
        return 

    @logwrap
    def _glGetProgramiv(self, *args):
        logging.error("_glGetProgramiv not implemented")
        return 

    @logwrap
    def _glGetRenderbufferParameteriv(self, *args):
        logging.error("_glGetRenderbufferParameteriv not implemented")
        return 

    @logwrap
    def _glGetShaderInfoLog(self, *args):
        logging.error("_glGetShaderInfoLog not implemented")
        return 

    @logwrap
    def _glGetShaderPrecisionFormat(self, *args):
        logging.error("_glGetShaderPrecisionFormat not implemented")
        return 

    @logwrap
    def _glGetShaderSource(self, *args):
        logging.error("_glGetShaderSource not implemented")
        return 

    @logwrap
    def _glGetShaderiv(self, *args):
        logging.error("_glGetShaderiv not implemented")
        return 

    @logwrap
    def _glGetString(self,name_):
        if name_ in self.GL.stringCache:
            return self.GL.stringCache[name_]
        
        if name_ in [7936, 7937, 37445, 37446]:
            arr = self.intArrayFromString(self.GL.ctx_getParameter(name_))
            ret = self.allocate(arr, "i8", self.ALLOC_NORMAL)

        elif name_ == 7938:
            # Get OpenGL version
            glVersion = self.GL.ctx_getParameter(self.GLctx_VERSION)
            glVersion = "OpenGL ES 3.0 (" + glVersion + ")"
            ret = self.allocate(self.intArrayFromString(glVersion), "i8", self.ALLOC_NORMAL)

        elif name_ == 7939:
            # Get supported extensions
            exts = self.GLctx_getSupportedExtensions
            gl_exts = []
            for ext in exts:
                gl_exts.append(ext)
                gl_exts.append("GL_" + ext)
            arr = self.intArrayFromString(" ".join(gl_exts))
            ret = self.allocate(arr, "i8", self.ALLOC_NORMAL)

        elif name_ == 35724:
            # Get GLSL version
            glslVersion = self.GL.ctx_getParameter(self.GLctx_SHADING_LANGUAGE_VERSION)
            assert(glslVersion is not None)
            ver_re = r"^WebGL GLSL ES ([0-9]\.[0-9][0-9]?)(?:$| .*)"
            ver_num = re.match(ver_re, glslVersion)
            if ver_num:
                ver_num = ver_num.group(1)
                if len(ver_num) == 3:
                    ver_num = ver_num + "0"
                glslVersion = "OpenGL ES GLSL ES " + ver_num + " (" + glslVersion + ")"
            arr = self.intArrayFromString(glslVersion)
            ret = self.allocate(arr, "i8", self.ALLOC_NORMAL)

        else:
            self.GL.lastError = 1280
            return 0
        self.GL.stringCache[name_] = ret
        return ret

    @logwrap
    def _glGetStringi(self, name, index):
        stringiCache = self.GL.stringiCache.get(name)
        
        if stringiCache:
            if index < 0 or index >= len(stringiCache):
                self.GL.lastError = 1281
                return 0
            return stringiCache[index]

        if name == 7939:
            exts = self.GLctx_getSupportedExtensions
            gl_exts = []
            for ext in exts:
                # Allocate both raw and prefixed extension names
                arr = self.intArrayFromString(ext)
                ret = self.allocate(arr, "i8", self.ALLOC_NORMAL)
                gl_exts.append(ret)

                arr = self.intArrayFromString("GL_" + ext)
                ret = self.allocate(arr, "i8", self.ALLOC_NORMAL)
                gl_exts.append(ret)
            
            self.GL.stringiCache[name] = gl_exts
            stringiCache = gl_exts

            if index < 0 or index >= len(stringiCache):
                self.GL.lastError = 1281
                return 0
            return stringiCache[index]

        # Handle unsupported name values
        self.GL.lastError = 1280
        return 0
    

    @logwrap
    def _glGetTexParameteriv(self,target, pname, params):
        if not params:
            self.GL.lastError = 1281
            return 
        
        self.HEAP32[params >> 2] = self.GL.ctx_getTexParameter(target, pname)
    

    @logwrap
    def _glGetUniformBlockIndex(self, *args):
        logging.error("_glGetUniformBlockIndex not implemented")
        return 0

    @logwrap
    def _glGetUniformIndices(self, *args):
        logging.error("_glGetUniformIndices not implemented")
        return 

    @logwrap
    def _glGetUniformLocation(self, *args):
        logging.error("_glGetUniformLocation not implemented")
        return 0

    @logwrap
    def _glGetUniformiv(self, *args):
        logging.error("_glGetUniformiv not implemented")
        return 

    @logwrap
    def _glGetVertexAttribiv(self, *args):
        logging.error("_glGetVertexAttribiv not implemented")
        return 

    @logwrap
    def _glInvalidateFramebuffer(self, *args):
        logging.error("_glInvalidateFramebuffer not implemented")
        return 

    @logwrap
    def _glIsEnabled(self, *args):
        logging.error("_glIsEnabled not implemented")
        return 0

    @logwrap
    def _glIsVertexArray(self, *args):
        logging.error("_glIsVertexArray not implemented")
        return 0

    @logwrap
    def _glLinkProgram(self, *args):
        logging.error("_glLinkProgram not implemented")
        return 

    @logwrap
    def _glMapBufferRange(self, *args):
        logging.error("_glMapBufferRange not implemented")
        return 0

    @logwrap
    def _glPixelStorei(self, *args):
        logging.error("_glPixelStorei not implemented")
        return 

    @logwrap
    def _glPolygonOffset(self, *args):
        logging.error("_glPolygonOffset not implemented")
        return 

    @logwrap
    def _glProgramBinary(self, *args):
        logging.error("_glProgramBinary not implemented")
        return 

    @logwrap
    def _glProgramParameteri(self, *args):
        logging.error("_glProgramParameteri not implemented")
        return 

    @logwrap
    def _glReadBuffer(self, *args):
        logging.error("_glReadBuffer not implemented")
        return 

    @logwrap
    def _glReadPixels(self, *args):
        logging.error("_glReadPixels not implemented")
        return 

    @logwrap
    def _glRenderbufferStorage(self, *args):
        logging.error("_glRenderbufferStorage not implemented")
        return 

    @logwrap
    def _glRenderbufferStorageMultisample(self, *args):
        logging.error("_glRenderbufferStorageMultisample not implemented")
        return 

    @logwrap
    def _glSamplerParameteri(self, *args):
        logging.error("_glSamplerParameteri not implemented")
        return 

    @logwrap
    def _glScissor(self, *args):
        logging.error("_glScissor not implemented")
        return 

    @logwrap
    def _glShaderSource(self, *args):
        logging.error("_glShaderSource not implemented")
        return 

    @logwrap
    def _glStencilFuncSeparate(self, *args):
        logging.error("_glStencilFuncSeparate not implemented")
        return 

    @logwrap
    def _glStencilMask(self, *args):
        logging.error("_glStencilMask not implemented")
        return 

    @logwrap
    def _glStencilOpSeparate(self, *args):
        logging.error("_glStencilOpSeparate not implemented")
        return 

    @logwrap
    def _glTexImage2D(self, *args):
        logging.error("_glTexImage2D not implemented")
        return 

    @logwrap
    def _glTexImage3D(self, *args):
        logging.error("_glTexImage3D not implemented")
        return 

    @logwrap
    def _glTexParameterf(self,param0,param1,param2):
        self.GL.ctx_setTexParameter(param0, param1, param2)
        return 
    
    @logwrap
    def _glTexParameteri(self,param0,param1,param2):
        self.GL.ctx_setTexParameter(param0, param1, param2)
    
    @logwrap
    def _glTexParameteriv(self,target, pname, params):
        param = self.HEAP32[params >> 2];
        self.GL.ctx_setTexParameter(target, pname, param)
    

    @logwrap
    def _glTexStorage2D(self,param0,param1,param2,param3,param4):
        logging.warning("_glTexStorage2D -- ignored")
        return 
    
    @logwrap
    def _glTexStorage3D(self,param0,param1,param2,param3,param4,param5):
        logging.warning("_glTexStorage3D -- ignored")
        return 
    
    @logwrap
    def _glTexSubImage2D(self,param0,param1,param2,param3,param4,param5,param6,param7,param8):
        logging.warning("_glTexSubImage2D -- ignored")
        return 
    
    @logwrap
    def _glTexSubImage3D(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
        logging.warning("_glTexSubImage3D -- ignored")
        return 
    
    @logwrap
    def _glTransformFeedbackVaryings(self,param0,param1,param2,param3):
        logging.warning("_glTransformFeedbackVaryings -- ignored")
        return 

    @logwrap
    def _glUniform1fv(self,param0,param1,param2):
        return 
    
    @logwrap
    def _glUniform1i(self,param0,param1):
        return 
    
    @logwrap
    def _glUniform1iv(self,param0,param1,param2):
        logging.error("_glUniform1iv not implemented")
        return 
    
    @logwrap
    def _glUniform1uiv(self,param0,param1,param2):
        logging.error("_glUniform1uiv not implemented")
        return 
    

    @logwrap
    def _glUniform2fv(self, *args):
        logging.error("_glUniform2fv not implemented")
        return 

    @logwrap
    def _glUniform2iv(self, *args):
        logging.error("_glUniform2iv not implemented")
        return 

    @logwrap
    def _glUniform2uiv(self, *args):
        logging.error("_glUniform2uiv not implemented")
        return 

    @logwrap
    def _glUniform3fv(self, *args):
        logging.error("_glUniform3fv not implemented")
        return 

    @logwrap
    def _glUniform3iv(self, *args):
        logging.error("_glUniform3iv not implemented")
        return 

    @logwrap
    def _glUniform3uiv(self, *args):
        logging.error("_glUniform3uiv not implemented")
        return 

    @logwrap
    def _glUniform4fv(self, *args):
        logging.error("_glUniform4fv not implemented")
        return 

    @logwrap
    def _glUniform4iv(self, *args):
        logging.error("_glUniform4iv not implemented")
        return 

    @logwrap
    def _glUniform4uiv(self, *args):
        logging.error("_glUniform4uiv not implemented")
        return 

    @logwrap
    def _glUniformBlockBinding(self, *args):
        logging.error("_glUniformBlockBinding not implemented")
        return 

    @logwrap
    def _glUniformMatrix3fv(self, *args):
        logging.error("_glUniformMatrix3fv not implemented")
        return 

    @logwrap
    def _glUniformMatrix4fv(self, *args):
        logging.error("_glUniformMatrix4fv not implemented")
        return 

    @logwrap
    def _glUnmapBuffer(self, *args):
        logging.error("_glUnmapBuffer not implemented")
        return 0

    @logwrap
    def _glUseProgram(self, *args):
        logging.error("_glUseProgram not implemented")
        return 

    @logwrap
    def _glValidateProgram(self, *args):
        logging.error("_glValidateProgram not implemented")
        return 

    @logwrap
    def _glVertexAttrib4f(self, *args):
        logging.error("_glVertexAttrib4f not implemented")
        return 

    @logwrap
    def _glVertexAttrib4fv(self, *args):
        logging.error("_glVertexAttrib4fv not implemented")
        return 

    @logwrap
    def _glVertexAttribIPointer(self, *args):
        logging.error("_glVertexAttribIPointer not implemented")
        return 

    @logwrap
    def _glVertexAttribPointer(self, *args):
        logging.error("_glVertexAttribPointer not implemented")
        return 

    @logwrap
    def _glViewport(self,param0,param1,param2,param3):
        logging.warning("_glViewport -- ignored")
        return 
    

    @logwrap
    def _gmtime(self,time_addr):
        tm_ptr = self.tm_current
        # Retrieve the timestamp in seconds
        timestamp = self.HEAP32[time_addr >> 2]
        
        # Convert timestamp to UTC datetime
        date = datetime.datetime.utcfromtimestamp(timestamp)
        
        # Store individual components into HEAP32
        self.HEAP32[tm_ptr >> 2] = date.second
        self.HEAP32[(tm_ptr + 4) >> 2] = date.minute
        self.HEAP32[(tm_ptr + 8) >> 2] = date.hour
        self.HEAP32[(tm_ptr + 12) >> 2] = date.day
        self.HEAP32[(tm_ptr + 16) >> 2] = date.month - 1  # JavaScript months are 0-11, Python is 1-12
        self.HEAP32[(tm_ptr + 20) >> 2] = date.year - 1900
        self.HEAP32[(tm_ptr + 24) >> 2] = date.weekday()  # Monday = 0, Sunday = 6 in Python
        self.HEAP32[(tm_ptr + 36) >> 2] = 0
        self.HEAP32[(tm_ptr + 32) >> 2] = 0
        
        # Calculate the day of the year (yday)
        start = datetime.datetime(date.year, 1, 1)
        yday = (date - start).days
        self.HEAP32[(tm_ptr + 28) >> 2] = yday
        self.HEAP32[(tm_ptr + 40) >> 2] = self.tm_timezone
        return tm_ptr

    @logwrap
    def _inet_addr(self, *args):
        logging.error("_inet_addr not implemented")
        return 0

    @logwrap
    def _llvm_eh_typeid_for(self,param0):
        return param0

    @logwrap
    def _llvm_exp2_f32(self,param0):
        return math.pow(2, param0)

    @logwrap
    def _llvm_log10_f32(self,param0):
        return math.log(param0) / math.log(10)

    @logwrap
    def _llvm_log10_f64(self,param0):
        logging.error("_llvm_log10_f64 not implemented")
        return 0
    
    @logwrap
    def _llvm_log2_f32(self,param0):
        return math.log(param0) / math.log(2)
    
    @logwrap
    def _llvm_trap(self):
        logging.error("_llvm_trap not implemented")
        return 

    @logwrap
    def _llvm_trunc_f32(self, *args):
        logging.error("_llvm_trunc_f32 not implemented")
        return 0

    
    @logwrap
    def _localtime(self,time_addr):
        self._tzset()
        tmPtr = self.tm_current
        predate = self.HEAP32[time_addr >> 2]
        date = datetime.datetime.fromtimestamp(predate)
        self.HEAP32[ tmPtr >> 2] = date.second
        self.HEAP32[(tmPtr + 4 )>> 2] = date.minute
        self.HEAP32[(tmPtr + 8 )>> 2] = date.hour
        self.HEAP32[(tmPtr + 12 )>> 2] = date.day
        self.HEAP32[(tmPtr + 16 )>> 2] = date.month - 1
        self.HEAP32[(tmPtr + 20 )>> 2] = date.year - 1900
        self.HEAP32[(tmPtr + 24 )>> 2] = date.weekday()

        start_of_year = datetime.datetime(date.year, 1, 1)
        yday = (date - start_of_year).days
        self.HEAP32[(tmPtr + 28) >> 2] = yday

        TIME_OFFSET = -480
        self.HEAP32[(tmPtr + 36 )>> 2] = -(TIME_OFFSET* 60)
        summerOffset = TIME_OFFSET
        winterOffset = TIME_OFFSET
        dst = 0
        self.HEAP32[(tmPtr + 32) >> 2] = dst
        zonePtr = self.HEAP32[self._get_tzname() + (4 if dst else 0) >> 2]
        self.HEAP32[tmPtr + 40 >> 2] = zonePtr
        return tmPtr

    @logwrap
    def _longjmp(self,param0,param1):
        logging.error("_longjmp not implemented")
        return 

    def _tzset(self):
        if self._tzset_called:
            return
        self._tzset_called =True

        # Set timezone offset in seconds
        self.HEAP32[self._get_timezone() >> 2] = time.timezone

        # Calculate daylight saving time
        current_year = datetime.datetime.now().year
        self.HEAP32[self._get_daylight() >> 2] = 0

        winter_name = 'Malaysia Time'
        summer_name = 'Malaysia Time'

        # Allocate memory for the timezone names
        winter_name_ptr = self.allocate(self.intArrayFromString(winter_name), "i8", self.ALLOC_NORMAL)
        summer_name_ptr = self.allocate(self.intArrayFromString(summer_name), "i8", self.ALLOC_NORMAL)

        self.HEAP32[self._get_tzname() >> 2] = summer_name_ptr
        self.HEAP32[(self._get_tzname() + 4) >> 2] = winter_name_ptr
    

    @logwrap
    def _mktime(self,tm_ptr):
        self._tzset()
        date = datetime.datetime(
            self.HEAP32[(tm_ptr + 20) >> 2] + 1900,  # Year
            self.HEAP32[(tm_ptr + 16) >> 2] + 1,     # Month (Python is 1-12, JS is 0-11)
            self.HEAP32[(tm_ptr + 12) >> 2],         # Day
            self.HEAP32[(tm_ptr + 8) >> 2],          # Hour
            self.HEAP32[(tm_ptr + 4) >> 2],          # Minute
            self.HEAP32[tm_ptr >> 2],                # Second
        )

        # Daylight Saving Time adjustment
        TIME_OFFSET = -480
        dst = self.HEAP32[(tm_ptr + 32) >> 2]
        guessed_offset = TIME_OFFSET
        
        start = datetime.datetime(date.year, 1, 1)
        summer = datetime.datetime(date.year, 7, 1)
        
        winter_offset = TIME_OFFSET
        summer_offset = TIME_OFFSET
        
        dst_offset = min(winter_offset, summer_offset)

        # Update day of week and day of year
        self.HEAP32[(tm_ptr + 24) >> 2] = date.weekday()
        yday = (date - start).days
        self.HEAP32[(tm_ptr + 28) >> 2] = yday

        # Return timestamp in seconds
        return int(date.timestamp())
    @logwrap
    def _pthread_cond_destroy(self, *args):
        logging.error("_pthread_cond_destroy not implemented")
        return 0

    @logwrap
    def _pthread_cond_init(self, *args):
        logging.error("_pthread_cond_init not implemented")
        return 0

    @logwrap
    def _pthread_cond_timedwait(self, *args):
        logging.error("_pthread_cond_timedwait not implemented")
        return 0

    @logwrap
    def _pthread_cond_wait(self, *args):
        logging.error("_pthread_cond_wait not implemented")
        return 0

    @logwrap
    def _pthread_getspecific(self, *args):
        logging.error("_pthread_getspecific not implemented")
        return 0

    @logwrap
    def _pthread_key_create(self, *args):
        logging.error("_pthread_key_create not implemented")
        return 0

    @logwrap
    def _pthread_key_delete(self, *args):
        logging.error("_pthread_key_delete not implemented")
        return 0

    @logwrap
    def _pthread_mutex_destroy(self, *args):
        logging.error("_pthread_mutex_destroy not implemented")
        return 0

    @logwrap
    def _pthread_mutex_init(self, *args):
        logging.error("_pthread_mutex_init not implemented")
        return 0

    @logwrap
    def _pthread_mutexattr_destroy(self, *args):
        logging.error("_pthread_mutexattr_destroy not implemented")
        return 0

    @logwrap
    def _pthread_mutexattr_init(self, *args):
        logging.error("_pthread_mutexattr_init not implemented")
        return 0

    @logwrap
    def _pthread_mutexattr_setprotocol(self, *args):
        logging.error("_pthread_mutexattr_setprotocol not implemented")
        return 0

    @logwrap
    def _pthread_mutexattr_settype(self, *args):
        logging.error("_pthread_mutexattr_settype not implemented")
        return 0

    @logwrap
    def _pthread_once(self, *args):
        logging.error("_pthread_once not implemented")
        return 0

    @logwrap
    def _pthread_setspecific(self, *args):
        logging.error("_pthread_setspecific not implemented")
        return 0

    @logwrap
    def _sched_yield(self, *args):
        logging.error("_sched_yield not implemented")
        return 0

    @logwrap
    def _setenv(self, *args):
        logging.error("_setenv not implemented")
        return 0

    @logwrap
    def _sigaction(self, *args):
        logging.error("_sigaction not implemented")
        return 0

    @logwrap
    def _sigemptyset(self, *args):
        logging.error("_sigemptyset not implemented")
        return 0

    @logwrap
    def _strftime(self, *args):
        logging.error("_strftime not implemented")
        return 0

    @logwrap
    def _sysconf(self, *args):
        logging.error("_sysconf not implemented")
        return 0

    @logwrap
    def _time(self,ptr):
        ret = int(time.time())
        if ptr:
            self.HEAP32[ptr >> 2] = ret
        return ret

    @logwrap
    def _unsetenv(self, *args):
        logging.error("_unsetenv not implemented")
        return 0

    @logwrap
    def _utime(self, *args):
        logging.error("_utime not implemented")
        return 0

    @logwrap
    def f64_rem(self,x,y):
        return x % y

    @logwrap
    def invoke_iiiiij(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiij(*args)
        except:
            logging.error('invoke_iiiiij fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiijii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiijii(*args)
        except:
            logging.error('invoke_iiiijii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiijjii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiijjii(*args)
        except:
            logging.error('invoke_iiiijjii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiiji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiji(*args)
        except:
            logging.error('invoke_iiiji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiijiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiijiii(*args)
        except:
            logging.error('invoke_iiijiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iij(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iij(*args)
        except:
            logging.error('invoke_iij fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iiji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iiji(*args)
        except:
            logging.error('invoke_iiji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_iijii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_iijii(*args)
        except:
            logging.error('invoke_iijii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_ijii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_ijii(*args)
        except:
            logging.error('invoke_ijii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_j(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_j(*args)
        except:
            logging.error('invoke_j fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jdi(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jdi(*args)
        except:
            logging.error('invoke_jdi fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_ji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_ji(*args)
        except:
            logging.error('invoke_ji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jii(*args)
        except:
            logging.error('invoke_jii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jiii(*args)
        except:
            logging.error('invoke_jiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jiiii(*args)
        except:
            logging.error('invoke_jiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jiiiii(*args)
        except:
            logging.error('invoke_jiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jiiiiiiiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jiiiiiiiiii(*args)
        except:
            logging.error('invoke_jiiiiiiiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jiiij(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jiiij(*args)
        except:
            logging.error('invoke_jiiij fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jiiji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jiiji(*args)
        except:
            logging.error('invoke_jiiji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jiji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jiji(*args)
        except:
            logging.error('invoke_jiji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jijii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jijii(*args)
        except:
            logging.error('invoke_jijii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jijiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jijiii(*args)
        except:
            logging.error('invoke_jijiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jijj(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jijj(*args)
        except:
            logging.error('invoke_jijj fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_jji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_jji(*args)
        except:
            logging.error('invoke_jji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 0

    @logwrap
    def invoke_viiiiiiifjjfii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiiiiifjjfii(*args)
        except:
            logging.error('invoke_viiiiiiifjjfii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiijiiii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiijiiii(*args)
        except:
            logging.error('invoke_viiiijiiii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiij(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiij(*args)
        except:
            logging.error('invoke_viiij fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiiji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiiji(*args)
        except:
            logging.error('invoke_viiiji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viij(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viij(*args)
        except:
            logging.error('invoke_viij fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viiji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viiji(*args)
        except:
            logging.error('invoke_viiji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viijji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viijji(*args)
        except:
            logging.error('invoke_viijji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_viji(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_viji(*args)
        except:
            logging.error('invoke_viji fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def invoke_vijii(self, *args):
        sp = self.stackSave()
        try:
            return self.dynCall_vijii(*args)
        except:
            logging.error('invoke_vijii fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)

        return 

    @logwrap
    def _atomic_fetch_add_8(self,ptr, vall, valh, memmodel):
        lo = int( self.HEAP32[ptr >> 2])
        hi = int(self.HEAP32[ptr + 4 >> 2])
        self.HEAP32[ptr >> 2] = self._i64Add(lo, hi, vall, valh)
        self.HEAP32[ptr + 4 >> 2] = self.getTempRet0()
        self.setTempRet0(hi)
        return lo

    @logwrap
    def _glClientWaitSync(self, *args):
        logging.error("_glClientWaitSync not implemented")
        return 0


    def export_wasm_func(self):
        self._growWasmMemory = partial(self.instance.exports(self.store)["__growWasmMemory"], self.store)
        self._SendMessage = partial(self.instance.exports(self.store)["_SendMessage"], self.store)
        self._SendMessageFloat = partial(self.instance.exports(self.store)["_SendMessageFloat"], self.store)
        self._SendMessageString = partial(self.instance.exports(self.store)["_SendMessageString"], self.store)
        self._SetFullscreen = partial(self.instance.exports(self.store)["_SetFullscreen"], self.store)
        self._GLOBAL_sub_I_AIScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AIScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_AccessibilityScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AccessibilityScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_AndroidJNIScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AndroidJNIScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_AnimationClip_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AnimationClip_cpp"], self.store)
        self._GLOBAL_sub_I_AnimationScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AnimationScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_AssetBundleFileSystem_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AssetBundleFileSystem_cpp"], self.store)
        self._GLOBAL_sub_I_AssetBundleScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AssetBundleScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_AudioScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AudioScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_Avatar_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Avatar_cpp"], self.store)
        self._GLOBAL_sub_I_ClothScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ClothScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_ConstraintManager_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ConstraintManager_cpp"], self.store)
        self._GLOBAL_sub_I_DirectorScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_DirectorScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_External_ProphecySDK_BlitOperations_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_External_ProphecySDK_BlitOperations_1_cpp"], self.store)
        self._GLOBAL_sub_I_External_Yoga_Yoga_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_External_Yoga_Yoga_0_cpp"], self.store)
        self._GLOBAL_sub_I_GUITexture_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_GUITexture_cpp"], self.store)
        self._GLOBAL_sub_I_GfxDeviceNull_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_GfxDeviceNull_cpp"], self.store)
        self._GLOBAL_sub_I_GridScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_GridScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_IMGUIScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_IMGUIScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_Il2CppCodeRegistration_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Il2CppCodeRegistration_cpp"], self.store)
        self._GLOBAL_sub_I_InputLegacyScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_InputLegacyScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_InputScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_InputScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_LogAssert_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_LogAssert_cpp"], self.store)
        self._GLOBAL_sub_I_Lump_libil2cpp_gc_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_gc_cpp"], self.store)
        self._GLOBAL_sub_I_Lump_libil2cpp_metadata_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_metadata_cpp"], self.store)
        self._GLOBAL_sub_I_Lump_libil2cpp_os_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_os_cpp"], self.store)
        self._GLOBAL_sub_I_Lump_libil2cpp_utils_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_utils_cpp"], self.store)
        self._GLOBAL_sub_I_Lump_libil2cpp_vm_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_vm_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Animation_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Animation_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Animation_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Animation_3_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Animation_6_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Animation_6_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_AssetBundle_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_AssetBundle_Public_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Audio_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Audio_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Audio_Public_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_3_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Audio_Public_ScriptBindings_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_ScriptBindings_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Audio_Public_sound_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_sound_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Cloth_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Cloth_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_DSPGraph_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_DSPGraph_Public_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Grid_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Grid_Public_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_IMGUI_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_IMGUI_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_IMGUI_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_IMGUI_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Input_Private_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Input_Private_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_ParticleSystem_Modules_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_ParticleSystem_Modules_3_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Physics2D_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Physics2D_Public_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Physics2D_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Physics2D_Public_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Physics_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Physics_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Physics_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Physics_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Profiler_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Profiler_Public_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Profiler_Runtime_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Profiler_Runtime_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Subsystems_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Subsystems_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Terrain_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_Public_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Terrain_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_Public_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Terrain_Public_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_Public_2_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Terrain_Public_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_Public_3_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Terrain_VR_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_VR_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_TextCore_Native_FontEngine_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_TextCore_Native_FontEngine_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_TextRendering_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_TextRendering_Public_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Tilemap_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Tilemap_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Tilemap_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Tilemap_Public_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_UI_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UI_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_UI_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UI_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_UI_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UI_2_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_UnityAnalytics_Dispatcher_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UnityAnalytics_Dispatcher_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_UnityWebRequest_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UnityWebRequest_Public_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_VFX_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_VFX_Public_1_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_VFX_Public_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_VFX_Public_2_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_VR_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_VR_2_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_VR_PluginInterface_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_VR_PluginInterface_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_Video_Public_Base_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Video_Public_Base_0_cpp"], self.store)
        self._GLOBAL_sub_I_Modules_XR_Subsystems_Input_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_XR_Subsystems_Input_Public_1_cpp"], self.store)
        self._GLOBAL_sub_I_ParticleSystemRenderer_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ParticleSystemRenderer_cpp"], self.store)
        self._GLOBAL_sub_I_ParticleSystemScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ParticleSystemScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_Physics2DScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Physics2DScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_PhysicsQuery_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PhysicsQuery_cpp"], self.store)
        self._GLOBAL_sub_I_PhysicsScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PhysicsScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_PlatformDependent_WebGL_External_baselib_builds_Source_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PlatformDependent_WebGL_External_baselib_builds_Source_0_cpp"], self.store)
        self._GLOBAL_sub_I_PlatformDependent_WebGL_Source_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PlatformDependent_WebGL_Source_0_cpp"], self.store)
        self._GLOBAL_sub_I_PlatformDependent_WebGL_Source_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PlatformDependent_WebGL_Source_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_2D_Renderer_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_2D_Renderer_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_2D_Sorting_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_2D_Sorting_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_2D_SpriteAtlas_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_2D_SpriteAtlas_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Allocator_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Allocator_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Allocator_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Allocator_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Application_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Application_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_BaseClasses_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_BaseClasses_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_BaseClasses_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_BaseClasses_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_BaseClasses_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_BaseClasses_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_BaseClasses_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_BaseClasses_3_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Burst_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Burst_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_3_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_4_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_5_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_6_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_6_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_7_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_7_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_Culling_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_Culling_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_RenderLoops_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_RenderLoops_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Camera_RenderLoops_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_RenderLoops_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Containers_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Containers_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Core_Callbacks_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Core_Callbacks_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Director_Core_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Director_Core_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_File_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_File_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Geometry_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Geometry_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_GfxDevice_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_GfxDevice_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_GfxDevice_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_3_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_GfxDevice_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_4_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_GfxDevice_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_5_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_GfxDevice_opengles_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_opengles_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_10_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_10_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_11_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_11_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_4_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_5_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_6_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_6_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_8_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_8_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_Billboard_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Billboard_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_LOD_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_LOD_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_Mesh_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_Mesh_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_Mesh_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_Mesh_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_4_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_Mesh_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_5_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Graphics_ScriptableRenderLoop_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_ScriptableRenderLoop_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Input_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Input_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Interfaces_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Interfaces_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Interfaces_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Interfaces_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Interfaces_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Interfaces_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Jobs_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Jobs_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Jobs_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Jobs_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Jobs_Internal_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Jobs_Internal_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Jobs_ScriptBindings_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Jobs_ScriptBindings_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Math_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Math_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Math_Random_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Math_Random_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Misc_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Misc_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Misc_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Misc_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Misc_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Misc_4_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Misc_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Misc_5_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Modules_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Modules_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Mono_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Mono_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_PluginInterface_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_PluginInterface_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_PreloadManager_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_PreloadManager_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Profiler_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Profiler_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Profiler_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Profiler_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Profiler_ScriptBindings_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Profiler_ScriptBindings_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_SceneManager_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_SceneManager_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_ScriptingBackend_Il2Cpp_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_ScriptingBackend_Il2Cpp_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Scripting_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Scripting_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Scripting_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Scripting_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_3_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Scripting_APIUpdating_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_APIUpdating_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Serialize_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Serialize_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Serialize_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Serialize_TransferFunctions_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Serialize_TransferFunctions_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Shaders_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Shaders_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Shaders_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Shaders_3_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Shaders_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Shaders_4_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Shaders_ShaderImpl_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Shaders_ShaderImpl_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Transform_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Transform_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Transform_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Transform_1_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Utilities_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_2_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Utilities_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_5_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Utilities_6_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_6_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Utilities_7_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_7_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Utilities_9_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_9_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_Video_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Video_0_cpp"], self.store)
        self._GLOBAL_sub_I_Runtime_VirtualFileSystem_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_VirtualFileSystem_0_cpp"], self.store)
        self._GLOBAL_sub_I_Shader_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Shader_cpp"], self.store)
        self._GLOBAL_sub_I_Shadows_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Shadows_cpp"], self.store)
        self._GLOBAL_sub_I_ShapeModule_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ShapeModule_cpp"], self.store)
        self._GLOBAL_sub_I_SubsystemsScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_SubsystemsScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_SwInterCollision_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_SwInterCollision_cpp"], self.store)
        self._GLOBAL_sub_I_SwSolverKernel_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_SwSolverKernel_cpp"], self.store)
        self._GLOBAL_sub_I_TemplateInstantiations_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TemplateInstantiations_cpp"], self.store)
        self._GLOBAL_sub_I_TerrainScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TerrainScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_TextCoreScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TextCoreScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_TextRenderingScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TextRenderingScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_TilemapScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TilemapScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_Transform_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Transform_cpp"], self.store)
        self._GLOBAL_sub_I_UIElementsScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UIElementsScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_UIScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UIScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_UnityAdsSettings_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UnityAdsSettings_cpp"], self.store)
        self._GLOBAL_sub_I_UnityAnalyticsScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UnityAnalyticsScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_UnityWebRequestScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UnityWebRequestScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_UnsafeUtility_bindings_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UnsafeUtility_bindings_cpp"], self.store)
        self._GLOBAL_sub_I_VFXScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_VFXScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_VRScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_VRScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_VideoScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_VideoScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_Wind_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Wind_cpp"], self.store)
        self._GLOBAL_sub_I_XRScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_XRScriptingClasses_cpp"], self.store)
        self._GLOBAL_sub_I_artifacts_WebGL_codegenerator_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_artifacts_WebGL_codegenerator_0_cpp"], self.store)
        self._GLOBAL_sub_I_nvcloth_src_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_nvcloth_src_0_cpp"], self.store)
        self._GLOBAL_sub_I_nvcloth_src_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_nvcloth_src_1_cpp"], self.store)
        self._GLOBAL_sub_I_umbra_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_umbra_cpp"], self.store)
        self._cxa_can_catch = partial(self.instance.exports(self.store)["___cxa_can_catch"], self.store)
        self._cxa_is_pointer_type = partial(self.instance.exports(self.store)["___cxa_is_pointer_type"], self.store)
        self._cxx_global_var_init = partial(self.instance.exports(self.store)["___cxx_global_var_init"], self.store)
        self._cxx_global_var_init_13 = partial(self.instance.exports(self.store)["___cxx_global_var_init_13"], self.store)
        self._cxx_global_var_init_131 = partial(self.instance.exports(self.store)["___cxx_global_var_init_131"], self.store)
        self._cxx_global_var_init_14 = partial(self.instance.exports(self.store)["___cxx_global_var_init_14"], self.store)
        self._cxx_global_var_init_15 = partial(self.instance.exports(self.store)["___cxx_global_var_init_15"], self.store)
        self._cxx_global_var_init_18 = partial(self.instance.exports(self.store)["___cxx_global_var_init_18"], self.store)
        self._cxx_global_var_init_22 = partial(self.instance.exports(self.store)["___cxx_global_var_init_22"], self.store)
        self._cxx_global_var_init_2_9504 = partial(self.instance.exports(self.store)["___cxx_global_var_init_2_9504"], self.store)
        self._cxx_global_var_init_3893 = partial(self.instance.exports(self.store)["___cxx_global_var_init_3893"], self.store)
        self._cxx_global_var_init_69 = partial(self.instance.exports(self.store)["___cxx_global_var_init_69"], self.store)
        self._cxx_global_var_init_7 = partial(self.instance.exports(self.store)["___cxx_global_var_init_7"], self.store)
        self._cxx_global_var_init_8100 = partial(self.instance.exports(self.store)["___cxx_global_var_init_8100"], self.store)
        self._cxx_global_var_init_98 = partial(self.instance.exports(self.store)["___cxx_global_var_init_98"], self.store)
        self._emscripten_environ_constructor = partial(self.instance.exports(self.store)["___emscripten_environ_constructor"], self.store)
        self._errno_location = partial(self.instance.exports(self.store)["___errno_location"], self.store)
        self._get_daylight = partial(self.instance.exports(self.store)["__get_daylight"], self.store)
        self._get_environ = partial(self.instance.exports(self.store)["__get_environ"], self.store)
        self._get_timezone = partial(self.instance.exports(self.store)["__get_timezone"], self.store)
        self._get_tzname = partial(self.instance.exports(self.store)["__get_tzname"], self.store)
        self._free = partial(self.instance.exports(self.store)["_free"], self.store)
        self._htonl = partial(self.instance.exports(self.store)["_htonl"], self.store)
        self._htons = partial(self.instance.exports(self.store)["_htons"], self.store)
        self._i64Add = partial(self.instance.exports(self.store)["_i64Add"], self.store)
        self._llvm_bswap_i16 = partial(self.instance.exports(self.store)["_llvm_bswap_i16"], self.store)
        self._llvm_bswap_i32 = partial(self.instance.exports(self.store)["_llvm_bswap_i32"], self.store)
        self._llvm_ctlz_i64 = partial(self.instance.exports(self.store)["_llvm_ctlz_i64"], self.store)
        self._llvm_ctpop_i32 = partial(self.instance.exports(self.store)["_llvm_ctpop_i32"], self.store)
        self._llvm_maxnum_f32 = partial(self.instance.exports(self.store)["_llvm_maxnum_f32"], self.store)
        self._llvm_maxnum_f64 = partial(self.instance.exports(self.store)["_llvm_maxnum_f64"], self.store)
        self._llvm_minnum_f32 = partial(self.instance.exports(self.store)["_llvm_minnum_f32"], self.store)
        self._llvm_round_f32 = partial(self.instance.exports(self.store)["_llvm_round_f32"], self.store)
        self._main = partial(self.instance.exports(self.store)["_main"], self.store)
        self._malloc = partial(self.instance.exports(self.store)["_malloc"], self.store)
        self._memalign = partial(self.instance.exports(self.store)["_memalign"], self.store)
        self._memcpy = partial(self.instance.exports(self.store)["_memcpy"], self.store)
        self._memmove = partial(self.instance.exports(self.store)["_memmove"], self.store)
        self._memset = partial(self.instance.exports(self.store)["_memset"], self.store)
        self._ntohs = partial(self.instance.exports(self.store)["_ntohs"], self.store)
        self._pthread_cond_broadcast = partial(self.instance.exports(self.store)["_pthread_cond_broadcast"], self.store)
        self._pthread_mutex_lock = partial(self.instance.exports(self.store)["_pthread_mutex_lock"], self.store)
        self._pthread_mutex_unlock = partial(self.instance.exports(self.store)["_pthread_mutex_unlock"], self.store)
        self._realloc = partial(self.instance.exports(self.store)["_realloc"], self.store)
        self._rintf = partial(self.instance.exports(self.store)["_rintf"], self.store)
        self._saveSetjmp = partial(self.instance.exports(self.store)["_saveSetjmp"], self.store)
        self._sbrk = partial(self.instance.exports(self.store)["_sbrk"], self.store)
        self._strlen = partial(self.instance.exports(self.store)["_strlen"], self.store)
        self._testSetjmp = partial(self.instance.exports(self.store)["_testSetjmp"], self.store)
        self.dynCall_dddi = partial(self.instance.exports(self.store)["dynCall_dddi"], self.store)
        self.dynCall_ddi = partial(self.instance.exports(self.store)["dynCall_ddi"], self.store)
        self.dynCall_ddidi = partial(self.instance.exports(self.store)["dynCall_ddidi"], self.store)
        self.dynCall_ddii = partial(self.instance.exports(self.store)["dynCall_ddii"], self.store)
        self.dynCall_ddiii = partial(self.instance.exports(self.store)["dynCall_ddiii"], self.store)
        self.dynCall_dfi = partial(self.instance.exports(self.store)["dynCall_dfi"], self.store)
        self.dynCall_di = partial(self.instance.exports(self.store)["dynCall_di"], self.store)
        self.dynCall_diddi = partial(self.instance.exports(self.store)["dynCall_diddi"], self.store)
        self.dynCall_didi = partial(self.instance.exports(self.store)["dynCall_didi"], self.store)
        self.dynCall_dii = partial(self.instance.exports(self.store)["dynCall_dii"], self.store)
        self.dynCall_diidi = partial(self.instance.exports(self.store)["dynCall_diidi"], self.store)
        self.dynCall_diii = partial(self.instance.exports(self.store)["dynCall_diii"], self.store)
        self.dynCall_diiid = partial(self.instance.exports(self.store)["dynCall_diiid"], self.store)
        self.dynCall_diiii = partial(self.instance.exports(self.store)["dynCall_diiii"], self.store)
        self.dynCall_diiiii = partial(self.instance.exports(self.store)["dynCall_diiiii"], self.store)
        self.dynCall_dij = partial(self.instance.exports(self.store)["dynCall_dij"], self.store)
        self.dynCall_diji = partial(self.instance.exports(self.store)["dynCall_diji"], self.store)
        self.dynCall_dji = partial(self.instance.exports(self.store)["dynCall_dji"], self.store)
        self.dynCall_f = partial(self.instance.exports(self.store)["dynCall_f"], self.store)
        self.dynCall_fdi = partial(self.instance.exports(self.store)["dynCall_fdi"], self.store)
        self.dynCall_ff = partial(self.instance.exports(self.store)["dynCall_ff"], self.store)
        self.dynCall_fff = partial(self.instance.exports(self.store)["dynCall_fff"], self.store)
        self.dynCall_ffff = partial(self.instance.exports(self.store)["dynCall_ffff"], self.store)
        self.dynCall_fffff = partial(self.instance.exports(self.store)["dynCall_fffff"], self.store)
        self.dynCall_ffffffi = partial(self.instance.exports(self.store)["dynCall_ffffffi"], self.store)
        self.dynCall_fffffi = partial(self.instance.exports(self.store)["dynCall_fffffi"], self.store)
        self.dynCall_ffffi = partial(self.instance.exports(self.store)["dynCall_ffffi"], self.store)
        self.dynCall_ffffii = partial(self.instance.exports(self.store)["dynCall_ffffii"], self.store)
        self.dynCall_fffi = partial(self.instance.exports(self.store)["dynCall_fffi"], self.store)
        self.dynCall_fffiffffffi = partial(self.instance.exports(self.store)["dynCall_fffiffffffi"], self.store)
        self.dynCall_fffifffffi = partial(self.instance.exports(self.store)["dynCall_fffifffffi"], self.store)
        self.dynCall_fffifffi = partial(self.instance.exports(self.store)["dynCall_fffifffi"], self.store)
        self.dynCall_fffifi = partial(self.instance.exports(self.store)["dynCall_fffifi"], self.store)
        self.dynCall_fffii = partial(self.instance.exports(self.store)["dynCall_fffii"], self.store)
        self.dynCall_fffiii = partial(self.instance.exports(self.store)["dynCall_fffiii"], self.store)
        self.dynCall_ffi = partial(self.instance.exports(self.store)["dynCall_ffi"], self.store)
        self.dynCall_fi = partial(self.instance.exports(self.store)["dynCall_fi"], self.store)
        self.dynCall_fidi = partial(self.instance.exports(self.store)["dynCall_fidi"], self.store)
        self.dynCall_fif = partial(self.instance.exports(self.store)["dynCall_fif"], self.store)
        self.dynCall_fiff = partial(self.instance.exports(self.store)["dynCall_fiff"], self.store)
        self.dynCall_fiffffi = partial(self.instance.exports(self.store)["dynCall_fiffffi"], self.store)
        self.dynCall_fifffi = partial(self.instance.exports(self.store)["dynCall_fifffi"], self.store)
        self.dynCall_fiffi = partial(self.instance.exports(self.store)["dynCall_fiffi"], self.store)
        self.dynCall_fifi = partial(self.instance.exports(self.store)["dynCall_fifi"], self.store)
        self.dynCall_fifii = partial(self.instance.exports(self.store)["dynCall_fifii"], self.store)
        self.dynCall_fii = partial(self.instance.exports(self.store)["dynCall_fii"], self.store)
        self.dynCall_fiif = partial(self.instance.exports(self.store)["dynCall_fiif"], self.store)
        self.dynCall_fiifdi = partial(self.instance.exports(self.store)["dynCall_fiifdi"], self.store)
        self.dynCall_fiiffffi = partial(self.instance.exports(self.store)["dynCall_fiiffffi"], self.store)
        self.dynCall_fiiffi = partial(self.instance.exports(self.store)["dynCall_fiiffi"], self.store)
        self.dynCall_fiifi = partial(self.instance.exports(self.store)["dynCall_fiifi"], self.store)
        self.dynCall_fiifii = partial(self.instance.exports(self.store)["dynCall_fiifii"], self.store)
        self.dynCall_fiifji = partial(self.instance.exports(self.store)["dynCall_fiifji"], self.store)
        self.dynCall_fiii = partial(self.instance.exports(self.store)["dynCall_fiii"], self.store)
        self.dynCall_fiiif = partial(self.instance.exports(self.store)["dynCall_fiiif"], self.store)
        self.dynCall_fiiii = partial(self.instance.exports(self.store)["dynCall_fiiii"], self.store)
        self.dynCall_fiiiif = partial(self.instance.exports(self.store)["dynCall_fiiiif"], self.store)
        self.dynCall_fiiiii = partial(self.instance.exports(self.store)["dynCall_fiiiii"], self.store)
        self.dynCall_fiiiiii = partial(self.instance.exports(self.store)["dynCall_fiiiiii"], self.store)
        self.dynCall_fiiiiiifiifif = partial(self.instance.exports(self.store)["dynCall_fiiiiiifiifif"], self.store)
        self.dynCall_fiiiiiifiiiif = partial(self.instance.exports(self.store)["dynCall_fiiiiiifiiiif"], self.store)
        self.dynCall_fji = partial(self.instance.exports(self.store)["dynCall_fji"], self.store)
        self.dynCall_i = partial(self.instance.exports(self.store)["dynCall_i"], self.store)
        self.dynCall_idddi = partial(self.instance.exports(self.store)["dynCall_idddi"], self.store)
        self.dynCall_iddi = partial(self.instance.exports(self.store)["dynCall_iddi"], self.store)
        self.dynCall_iddii = partial(self.instance.exports(self.store)["dynCall_iddii"], self.store)
        self.dynCall_idi = partial(self.instance.exports(self.store)["dynCall_idi"], self.store)
        self.dynCall_idii = partial(self.instance.exports(self.store)["dynCall_idii"], self.store)
        self.dynCall_idiii = partial(self.instance.exports(self.store)["dynCall_idiii"], self.store)
        self.dynCall_idiiii = partial(self.instance.exports(self.store)["dynCall_idiiii"], self.store)
        self.dynCall_iffffffi = partial(self.instance.exports(self.store)["dynCall_iffffffi"], self.store)
        self.dynCall_iffffi = partial(self.instance.exports(self.store)["dynCall_iffffi"], self.store)
        self.dynCall_ifffi = partial(self.instance.exports(self.store)["dynCall_ifffi"], self.store)
        self.dynCall_iffi = partial(self.instance.exports(self.store)["dynCall_iffi"], self.store)
        self.dynCall_ifi = partial(self.instance.exports(self.store)["dynCall_ifi"], self.store)
        self.dynCall_ifii = partial(self.instance.exports(self.store)["dynCall_ifii"], self.store)
        self.dynCall_ifiii = partial(self.instance.exports(self.store)["dynCall_ifiii"], self.store)
        self.dynCall_ifiiii = partial(self.instance.exports(self.store)["dynCall_ifiiii"], self.store)
        self.dynCall_ii = partial(self.instance.exports(self.store)["dynCall_ii"], self.store)
        self.dynCall_iiddi = partial(self.instance.exports(self.store)["dynCall_iiddi"], self.store)
        self.dynCall_iidi = partial(self.instance.exports(self.store)["dynCall_iidi"], self.store)
        self.dynCall_iidii = partial(self.instance.exports(self.store)["dynCall_iidii"], self.store)
        self.dynCall_iidiii = partial(self.instance.exports(self.store)["dynCall_iidiii"], self.store)
        self.dynCall_iif = partial(self.instance.exports(self.store)["dynCall_iif"], self.store)
        self.dynCall_iiff = partial(self.instance.exports(self.store)["dynCall_iiff"], self.store)
        self.dynCall_iifff = partial(self.instance.exports(self.store)["dynCall_iifff"], self.store)
        self.dynCall_iiffffffiii = partial(self.instance.exports(self.store)["dynCall_iiffffffiii"], self.store)
        self.dynCall_iiffffi = partial(self.instance.exports(self.store)["dynCall_iiffffi"], self.store)
        self.dynCall_iiffffiii = partial(self.instance.exports(self.store)["dynCall_iiffffiii"], self.store)
        self.dynCall_iifffi = partial(self.instance.exports(self.store)["dynCall_iifffi"], self.store)
        self.dynCall_iifffiii = partial(self.instance.exports(self.store)["dynCall_iifffiii"], self.store)
        self.dynCall_iiffi = partial(self.instance.exports(self.store)["dynCall_iiffi"], self.store)
        self.dynCall_iiffifiii = partial(self.instance.exports(self.store)["dynCall_iiffifiii"], self.store)
        self.dynCall_iiffii = partial(self.instance.exports(self.store)["dynCall_iiffii"], self.store)
        self.dynCall_iiffiii = partial(self.instance.exports(self.store)["dynCall_iiffiii"], self.store)
        self.dynCall_iiffiiiii = partial(self.instance.exports(self.store)["dynCall_iiffiiiii"], self.store)
        self.dynCall_iifi = partial(self.instance.exports(self.store)["dynCall_iifi"], self.store)
        self.dynCall_iifii = partial(self.instance.exports(self.store)["dynCall_iifii"], self.store)
        self.dynCall_iifiifii = partial(self.instance.exports(self.store)["dynCall_iifiifii"], self.store)
        self.dynCall_iifiifiii = partial(self.instance.exports(self.store)["dynCall_iifiifiii"], self.store)
        self.dynCall_iifiii = partial(self.instance.exports(self.store)["dynCall_iifiii"], self.store)
        self.dynCall_iifiiii = partial(self.instance.exports(self.store)["dynCall_iifiiii"], self.store)
        self.dynCall_iifiiiii = partial(self.instance.exports(self.store)["dynCall_iifiiiii"], self.store)
        self.dynCall_iifiiiiii = partial(self.instance.exports(self.store)["dynCall_iifiiiiii"], self.store)
        self.dynCall_iii = partial(self.instance.exports(self.store)["dynCall_iii"], self.store)
        self.dynCall_iiiddi = partial(self.instance.exports(self.store)["dynCall_iiiddi"], self.store)
        self.dynCall_iiidi = partial(self.instance.exports(self.store)["dynCall_iiidi"], self.store)
        self.dynCall_iiidii = partial(self.instance.exports(self.store)["dynCall_iiidii"], self.store)
        self.dynCall_iiidiii = partial(self.instance.exports(self.store)["dynCall_iiidiii"], self.store)
        self.dynCall_iiif = partial(self.instance.exports(self.store)["dynCall_iiif"], self.store)
        self.dynCall_iiiffffi = partial(self.instance.exports(self.store)["dynCall_iiiffffi"], self.store)
        self.dynCall_iiifffi = partial(self.instance.exports(self.store)["dynCall_iiifffi"], self.store)
        self.dynCall_iiifffii = partial(self.instance.exports(self.store)["dynCall_iiifffii"], self.store)
        self.dynCall_iiiffi = partial(self.instance.exports(self.store)["dynCall_iiiffi"], self.store)
        self.dynCall_iiiffifiii = partial(self.instance.exports(self.store)["dynCall_iiiffifiii"], self.store)
        self.dynCall_iiiffii = partial(self.instance.exports(self.store)["dynCall_iiiffii"], self.store)
        self.dynCall_iiiffiii = partial(self.instance.exports(self.store)["dynCall_iiiffiii"], self.store)
        self.dynCall_iiifi = partial(self.instance.exports(self.store)["dynCall_iiifi"], self.store)
        self.dynCall_iiififi = partial(self.instance.exports(self.store)["dynCall_iiififi"], self.store)
        self.dynCall_iiififii = partial(self.instance.exports(self.store)["dynCall_iiififii"], self.store)
        self.dynCall_iiififiii = partial(self.instance.exports(self.store)["dynCall_iiififiii"], self.store)
        self.dynCall_iiififiiii = partial(self.instance.exports(self.store)["dynCall_iiififiiii"], self.store)
        self.dynCall_iiifii = partial(self.instance.exports(self.store)["dynCall_iiifii"], self.store)
        self.dynCall_iiifiifii = partial(self.instance.exports(self.store)["dynCall_iiifiifii"], self.store)
        self.dynCall_iiifiifiii = partial(self.instance.exports(self.store)["dynCall_iiifiifiii"], self.store)
        self.dynCall_iiifiifiiii = partial(self.instance.exports(self.store)["dynCall_iiifiifiiii"], self.store)
        self.dynCall_iiifiii = partial(self.instance.exports(self.store)["dynCall_iiifiii"], self.store)
        self.dynCall_iiifiiii = partial(self.instance.exports(self.store)["dynCall_iiifiiii"], self.store)
        self.dynCall_iiifiiiii = partial(self.instance.exports(self.store)["dynCall_iiifiiiii"], self.store)
        self.dynCall_iiii = partial(self.instance.exports(self.store)["dynCall_iiii"], self.store)
        self.dynCall_iiiifffffi = partial(self.instance.exports(self.store)["dynCall_iiiifffffi"], self.store)
        self.dynCall_iiiifffffii = partial(self.instance.exports(self.store)["dynCall_iiiifffffii"], self.store)
        self.dynCall_iiiiffffi = partial(self.instance.exports(self.store)["dynCall_iiiiffffi"], self.store)
        self.dynCall_iiiiffi = partial(self.instance.exports(self.store)["dynCall_iiiiffi"], self.store)
        self.dynCall_iiiiffii = partial(self.instance.exports(self.store)["dynCall_iiiiffii"], self.store)
        self.dynCall_iiiifi = partial(self.instance.exports(self.store)["dynCall_iiiifi"], self.store)
        self.dynCall_iiiififi = partial(self.instance.exports(self.store)["dynCall_iiiififi"], self.store)
        self.dynCall_iiiifii = partial(self.instance.exports(self.store)["dynCall_iiiifii"], self.store)
        self.dynCall_iiiifiii = partial(self.instance.exports(self.store)["dynCall_iiiifiii"], self.store)
        self.dynCall_iiiifiiii = partial(self.instance.exports(self.store)["dynCall_iiiifiiii"], self.store)
        self.dynCall_iiiifiiiii = partial(self.instance.exports(self.store)["dynCall_iiiifiiiii"], self.store)
        self.dynCall_iiiii = partial(self.instance.exports(self.store)["dynCall_iiiii"], self.store)
        self.dynCall_iiiiidii = partial(self.instance.exports(self.store)["dynCall_iiiiidii"], self.store)
        self.dynCall_iiiiifi = partial(self.instance.exports(self.store)["dynCall_iiiiifi"], self.store)
        self.dynCall_iiiiifii = partial(self.instance.exports(self.store)["dynCall_iiiiifii"], self.store)
        self.dynCall_iiiiifiii = partial(self.instance.exports(self.store)["dynCall_iiiiifiii"], self.store)
        self.dynCall_iiiiifiiiiif = partial(self.instance.exports(self.store)["dynCall_iiiiifiiiiif"], self.store)
        self.dynCall_iiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiii"], self.store)
        self.dynCall_iiiiiifff = partial(self.instance.exports(self.store)["dynCall_iiiiiifff"], self.store)
        self.dynCall_iiiiiifffiiifiii = partial(self.instance.exports(self.store)["dynCall_iiiiiifffiiifiii"], self.store)
        self.dynCall_iiiiiiffiiiiiiiiiffffiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiffiiiiiiiiiffffiii"], self.store)
        self.dynCall_iiiiiiffiiiiiiiiiffffiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiffiiiiiiiiiffffiiii"], self.store)
        self.dynCall_iiiiiiffiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiffiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiifi = partial(self.instance.exports(self.store)["dynCall_iiiiiifi"], self.store)
        self.dynCall_iiiiiifiif = partial(self.instance.exports(self.store)["dynCall_iiiiiifiif"], self.store)
        self.dynCall_iiiiiifiii = partial(self.instance.exports(self.store)["dynCall_iiiiiifiii"], self.store)
        self.dynCall_iiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiii"], self.store)
        self.dynCall_iiiiiiifiif = partial(self.instance.exports(self.store)["dynCall_iiiiiiifiif"], self.store)
        self.dynCall_iiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiii"], self.store)
        self.dynCall_iiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiij = partial(self.instance.exports(self.store)["dynCall_iiiiij"], self.store)
        self.dynCall_iiiiiji = partial(self.instance.exports(self.store)["dynCall_iiiiiji"], self.store)
        self.dynCall_iiiij = partial(self.instance.exports(self.store)["dynCall_iiiij"], self.store)
        self.dynCall_iiiiji = partial(self.instance.exports(self.store)["dynCall_iiiiji"], self.store)
        self.dynCall_iiiijii = partial(self.instance.exports(self.store)["dynCall_iiiijii"], self.store)
        self.dynCall_iiiijiiii = partial(self.instance.exports(self.store)["dynCall_iiiijiiii"], self.store)
        self.dynCall_iiiijjii = partial(self.instance.exports(self.store)["dynCall_iiiijjii"], self.store)
        self.dynCall_iiiijjiiii = partial(self.instance.exports(self.store)["dynCall_iiiijjiiii"], self.store)
        self.dynCall_iiij = partial(self.instance.exports(self.store)["dynCall_iiij"], self.store)
        self.dynCall_iiiji = partial(self.instance.exports(self.store)["dynCall_iiiji"], self.store)
        self.dynCall_iiijii = partial(self.instance.exports(self.store)["dynCall_iiijii"], self.store)
        self.dynCall_iiijiii = partial(self.instance.exports(self.store)["dynCall_iiijiii"], self.store)
        self.dynCall_iiijji = partial(self.instance.exports(self.store)["dynCall_iiijji"], self.store)
        self.dynCall_iiijjii = partial(self.instance.exports(self.store)["dynCall_iiijjii"], self.store)
        self.dynCall_iiijjiii = partial(self.instance.exports(self.store)["dynCall_iiijjiii"], self.store)
        self.dynCall_iiijjiiii = partial(self.instance.exports(self.store)["dynCall_iiijjiiii"], self.store)
        self.dynCall_iij = partial(self.instance.exports(self.store)["dynCall_iij"], self.store)
        self.dynCall_iiji = partial(self.instance.exports(self.store)["dynCall_iiji"], self.store)
        self.dynCall_iijii = partial(self.instance.exports(self.store)["dynCall_iijii"], self.store)
        self.dynCall_iijiii = partial(self.instance.exports(self.store)["dynCall_iijiii"], self.store)
        self.dynCall_iijiiii = partial(self.instance.exports(self.store)["dynCall_iijiiii"], self.store)
        self.dynCall_iijiiiiii = partial(self.instance.exports(self.store)["dynCall_iijiiiiii"], self.store)
        self.dynCall_iijji = partial(self.instance.exports(self.store)["dynCall_iijji"], self.store)
        self.dynCall_iijjii = partial(self.instance.exports(self.store)["dynCall_iijjii"], self.store)
        self.dynCall_iijjiii = partial(self.instance.exports(self.store)["dynCall_iijjiii"], self.store)
        self.dynCall_iijjji = partial(self.instance.exports(self.store)["dynCall_iijjji"], self.store)
        self.dynCall_ij = partial(self.instance.exports(self.store)["dynCall_ij"], self.store)
        self.dynCall_iji = partial(self.instance.exports(self.store)["dynCall_iji"], self.store)
        self.dynCall_ijii = partial(self.instance.exports(self.store)["dynCall_ijii"], self.store)
        self.dynCall_ijiii = partial(self.instance.exports(self.store)["dynCall_ijiii"], self.store)
        self.dynCall_ijiiii = partial(self.instance.exports(self.store)["dynCall_ijiiii"], self.store)
        self.dynCall_ijj = partial(self.instance.exports(self.store)["dynCall_ijj"], self.store)
        self.dynCall_ijji = partial(self.instance.exports(self.store)["dynCall_ijji"], self.store)
        self.dynCall_j = partial(self.instance.exports(self.store)["dynCall_j"], self.store)
        self.dynCall_jdi = partial(self.instance.exports(self.store)["dynCall_jdi"], self.store)
        self.dynCall_jdii = partial(self.instance.exports(self.store)["dynCall_jdii"], self.store)
        self.dynCall_jfi = partial(self.instance.exports(self.store)["dynCall_jfi"], self.store)
        self.dynCall_ji = partial(self.instance.exports(self.store)["dynCall_ji"], self.store)
        self.dynCall_jid = partial(self.instance.exports(self.store)["dynCall_jid"], self.store)
        self.dynCall_jidi = partial(self.instance.exports(self.store)["dynCall_jidi"], self.store)
        self.dynCall_jidii = partial(self.instance.exports(self.store)["dynCall_jidii"], self.store)
        self.dynCall_jii = partial(self.instance.exports(self.store)["dynCall_jii"], self.store)
        self.dynCall_jiii = partial(self.instance.exports(self.store)["dynCall_jiii"], self.store)
        self.dynCall_jiiii = partial(self.instance.exports(self.store)["dynCall_jiiii"], self.store)
        self.dynCall_jiiiii = partial(self.instance.exports(self.store)["dynCall_jiiiii"], self.store)
        self.dynCall_jiiiiii = partial(self.instance.exports(self.store)["dynCall_jiiiiii"], self.store)
        self.dynCall_jiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_jiiiiiiiii"], self.store)
        self.dynCall_jiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_jiiiiiiiiii"], self.store)
        self.dynCall_jiiij = partial(self.instance.exports(self.store)["dynCall_jiiij"], self.store)
        self.dynCall_jiiji = partial(self.instance.exports(self.store)["dynCall_jiiji"], self.store)
        self.dynCall_jiji = partial(self.instance.exports(self.store)["dynCall_jiji"], self.store)
        self.dynCall_jijii = partial(self.instance.exports(self.store)["dynCall_jijii"], self.store)
        self.dynCall_jijiii = partial(self.instance.exports(self.store)["dynCall_jijiii"], self.store)
        self.dynCall_jijj = partial(self.instance.exports(self.store)["dynCall_jijj"], self.store)
        self.dynCall_jijji = partial(self.instance.exports(self.store)["dynCall_jijji"], self.store)
        self.dynCall_jji = partial(self.instance.exports(self.store)["dynCall_jji"], self.store)
        self.dynCall_jjii = partial(self.instance.exports(self.store)["dynCall_jjii"], self.store)
        self.dynCall_jjji = partial(self.instance.exports(self.store)["dynCall_jjji"], self.store)
        self.dynCall_jjjji = partial(self.instance.exports(self.store)["dynCall_jjjji"], self.store)
        self.dynCall_v = partial(self.instance.exports(self.store)["dynCall_v"], self.store)
        self.dynCall_vd = partial(self.instance.exports(self.store)["dynCall_vd"], self.store)
        self.dynCall_vdi = partial(self.instance.exports(self.store)["dynCall_vdi"], self.store)
        self.dynCall_vf = partial(self.instance.exports(self.store)["dynCall_vf"], self.store)
        self.dynCall_vff = partial(self.instance.exports(self.store)["dynCall_vff"], self.store)
        self.dynCall_vfff = partial(self.instance.exports(self.store)["dynCall_vfff"], self.store)
        self.dynCall_vffff = partial(self.instance.exports(self.store)["dynCall_vffff"], self.store)
        self.dynCall_vfffffffffiiii = partial(self.instance.exports(self.store)["dynCall_vfffffffffiiii"], self.store)
        self.dynCall_vffffi = partial(self.instance.exports(self.store)["dynCall_vffffi"], self.store)
        self.dynCall_vfffi = partial(self.instance.exports(self.store)["dynCall_vfffi"], self.store)
        self.dynCall_vffi = partial(self.instance.exports(self.store)["dynCall_vffi"], self.store)
        self.dynCall_vfi = partial(self.instance.exports(self.store)["dynCall_vfi"], self.store)
        self.dynCall_vfii = partial(self.instance.exports(self.store)["dynCall_vfii"], self.store)
        self.dynCall_vfiii = partial(self.instance.exports(self.store)["dynCall_vfiii"], self.store)
        self.dynCall_vfiiiii = partial(self.instance.exports(self.store)["dynCall_vfiiiii"], self.store)
        self.dynCall_vi = partial(self.instance.exports(self.store)["dynCall_vi"], self.store)
        self.dynCall_vid = partial(self.instance.exports(self.store)["dynCall_vid"], self.store)
        self.dynCall_vidd = partial(self.instance.exports(self.store)["dynCall_vidd"], self.store)
        self.dynCall_vidddi = partial(self.instance.exports(self.store)["dynCall_vidddi"], self.store)
        self.dynCall_viddi = partial(self.instance.exports(self.store)["dynCall_viddi"], self.store)
        self.dynCall_viddiiii = partial(self.instance.exports(self.store)["dynCall_viddiiii"], self.store)
        self.dynCall_vidi = partial(self.instance.exports(self.store)["dynCall_vidi"], self.store)
        self.dynCall_vidii = partial(self.instance.exports(self.store)["dynCall_vidii"], self.store)
        self.dynCall_vidiii = partial(self.instance.exports(self.store)["dynCall_vidiii"], self.store)
        self.dynCall_vif = partial(self.instance.exports(self.store)["dynCall_vif"], self.store)
        self.dynCall_viff = partial(self.instance.exports(self.store)["dynCall_viff"], self.store)
        self.dynCall_vifff = partial(self.instance.exports(self.store)["dynCall_vifff"], self.store)
        self.dynCall_viffff = partial(self.instance.exports(self.store)["dynCall_viffff"], self.store)
        self.dynCall_viffffffffffffiiii = partial(self.instance.exports(self.store)["dynCall_viffffffffffffiiii"], self.store)
        self.dynCall_vifffffffi = partial(self.instance.exports(self.store)["dynCall_vifffffffi"], self.store)
        self.dynCall_viffffffi = partial(self.instance.exports(self.store)["dynCall_viffffffi"], self.store)
        self.dynCall_vifffffi = partial(self.instance.exports(self.store)["dynCall_vifffffi"], self.store)
        self.dynCall_viffffi = partial(self.instance.exports(self.store)["dynCall_viffffi"], self.store)
        self.dynCall_viffffii = partial(self.instance.exports(self.store)["dynCall_viffffii"], self.store)
        self.dynCall_viffffiifffiiiiif = partial(self.instance.exports(self.store)["dynCall_viffffiifffiiiiif"], self.store)
        self.dynCall_viffffiii = partial(self.instance.exports(self.store)["dynCall_viffffiii"], self.store)
        self.dynCall_vifffi = partial(self.instance.exports(self.store)["dynCall_vifffi"], self.store)
        self.dynCall_vifffii = partial(self.instance.exports(self.store)["dynCall_vifffii"], self.store)
        self.dynCall_viffi = partial(self.instance.exports(self.store)["dynCall_viffi"], self.store)
        self.dynCall_viffii = partial(self.instance.exports(self.store)["dynCall_viffii"], self.store)
        self.dynCall_viffiifffffiii = partial(self.instance.exports(self.store)["dynCall_viffiifffffiii"], self.store)
        self.dynCall_viffiii = partial(self.instance.exports(self.store)["dynCall_viffiii"], self.store)
        self.dynCall_viffiiifi = partial(self.instance.exports(self.store)["dynCall_viffiiifi"], self.store)
        self.dynCall_viffiiiif = partial(self.instance.exports(self.store)["dynCall_viffiiiif"], self.store)
        self.dynCall_vifi = partial(self.instance.exports(self.store)["dynCall_vifi"], self.store)
        self.dynCall_vififiii = partial(self.instance.exports(self.store)["dynCall_vififiii"], self.store)
        self.dynCall_vifii = partial(self.instance.exports(self.store)["dynCall_vifii"], self.store)
        self.dynCall_vifiii = partial(self.instance.exports(self.store)["dynCall_vifiii"], self.store)
        self.dynCall_vifiiii = partial(self.instance.exports(self.store)["dynCall_vifiiii"], self.store)
        self.dynCall_vifiiiii = partial(self.instance.exports(self.store)["dynCall_vifiiiii"], self.store)
        self.dynCall_vii = partial(self.instance.exports(self.store)["dynCall_vii"], self.store)
        self.dynCall_viid = partial(self.instance.exports(self.store)["dynCall_viid"], self.store)
        self.dynCall_viidd = partial(self.instance.exports(self.store)["dynCall_viidd"], self.store)
        self.dynCall_viidi = partial(self.instance.exports(self.store)["dynCall_viidi"], self.store)
        self.dynCall_viidii = partial(self.instance.exports(self.store)["dynCall_viidii"], self.store)
        self.dynCall_viif = partial(self.instance.exports(self.store)["dynCall_viif"], self.store)
        self.dynCall_viiff = partial(self.instance.exports(self.store)["dynCall_viiff"], self.store)
        self.dynCall_viifff = partial(self.instance.exports(self.store)["dynCall_viifff"], self.store)
        self.dynCall_viiffffffffi = partial(self.instance.exports(self.store)["dynCall_viiffffffffi"], self.store)
        self.dynCall_viiffffffffiii = partial(self.instance.exports(self.store)["dynCall_viiffffffffiii"], self.store)
        self.dynCall_viifffffffi = partial(self.instance.exports(self.store)["dynCall_viifffffffi"], self.store)
        self.dynCall_viiffffffi = partial(self.instance.exports(self.store)["dynCall_viiffffffi"], self.store)
        self.dynCall_viifffffi = partial(self.instance.exports(self.store)["dynCall_viifffffi"], self.store)
        self.dynCall_viiffffi = partial(self.instance.exports(self.store)["dynCall_viiffffi"], self.store)
        self.dynCall_viifffi = partial(self.instance.exports(self.store)["dynCall_viifffi"], self.store)
        self.dynCall_viiffi = partial(self.instance.exports(self.store)["dynCall_viiffi"], self.store)
        self.dynCall_viiffifiii = partial(self.instance.exports(self.store)["dynCall_viiffifiii"], self.store)
        self.dynCall_viiffii = partial(self.instance.exports(self.store)["dynCall_viiffii"], self.store)
        self.dynCall_viiffiifi = partial(self.instance.exports(self.store)["dynCall_viiffiifi"], self.store)
        self.dynCall_viiffiifiii = partial(self.instance.exports(self.store)["dynCall_viiffiifiii"], self.store)
        self.dynCall_viiffiiii = partial(self.instance.exports(self.store)["dynCall_viiffiiii"], self.store)
        self.dynCall_viiffiiiii = partial(self.instance.exports(self.store)["dynCall_viiffiiiii"], self.store)
        self.dynCall_viifi = partial(self.instance.exports(self.store)["dynCall_viifi"], self.store)
        self.dynCall_viififii = partial(self.instance.exports(self.store)["dynCall_viififii"], self.store)
        self.dynCall_viififiii = partial(self.instance.exports(self.store)["dynCall_viififiii"], self.store)
        self.dynCall_viifii = partial(self.instance.exports(self.store)["dynCall_viifii"], self.store)
        self.dynCall_viifiii = partial(self.instance.exports(self.store)["dynCall_viifiii"], self.store)
        self.dynCall_viifiiii = partial(self.instance.exports(self.store)["dynCall_viifiiii"], self.store)
        self.dynCall_viii = partial(self.instance.exports(self.store)["dynCall_viii"], self.store)
        self.dynCall_viiidi = partial(self.instance.exports(self.store)["dynCall_viiidi"], self.store)
        self.dynCall_viiif = partial(self.instance.exports(self.store)["dynCall_viiif"], self.store)
        self.dynCall_viiifffi = partial(self.instance.exports(self.store)["dynCall_viiifffi"], self.store)
        self.dynCall_viiifffiiij = partial(self.instance.exports(self.store)["dynCall_viiifffiiij"], self.store)
        self.dynCall_viiiffi = partial(self.instance.exports(self.store)["dynCall_viiiffi"], self.store)
        self.dynCall_viiiffii = partial(self.instance.exports(self.store)["dynCall_viiiffii"], self.store)
        self.dynCall_viiifi = partial(self.instance.exports(self.store)["dynCall_viiifi"], self.store)
        self.dynCall_viiififfi = partial(self.instance.exports(self.store)["dynCall_viiififfi"], self.store)
        self.dynCall_viiififi = partial(self.instance.exports(self.store)["dynCall_viiififi"], self.store)
        self.dynCall_viiififii = partial(self.instance.exports(self.store)["dynCall_viiififii"], self.store)
        self.dynCall_viiifii = partial(self.instance.exports(self.store)["dynCall_viiifii"], self.store)
        self.dynCall_viiifiii = partial(self.instance.exports(self.store)["dynCall_viiifiii"], self.store)
        self.dynCall_viiifiiiii = partial(self.instance.exports(self.store)["dynCall_viiifiiiii"], self.store)
        self.dynCall_viiii = partial(self.instance.exports(self.store)["dynCall_viiii"], self.store)
        self.dynCall_viiiiddi = partial(self.instance.exports(self.store)["dynCall_viiiiddi"], self.store)
        self.dynCall_viiiif = partial(self.instance.exports(self.store)["dynCall_viiiif"], self.store)
        self.dynCall_viiiiffffffi = partial(self.instance.exports(self.store)["dynCall_viiiiffffffi"], self.store)
        self.dynCall_viiiifffffi = partial(self.instance.exports(self.store)["dynCall_viiiifffffi"], self.store)
        self.dynCall_viiiiffffii = partial(self.instance.exports(self.store)["dynCall_viiiiffffii"], self.store)
        self.dynCall_viiiifffi = partial(self.instance.exports(self.store)["dynCall_viiiifffi"], self.store)
        self.dynCall_viiiiffiii = partial(self.instance.exports(self.store)["dynCall_viiiiffiii"], self.store)
        self.dynCall_viiiifi = partial(self.instance.exports(self.store)["dynCall_viiiifi"], self.store)
        self.dynCall_viiiififfi = partial(self.instance.exports(self.store)["dynCall_viiiififfi"], self.store)
        self.dynCall_viiiifii = partial(self.instance.exports(self.store)["dynCall_viiiifii"], self.store)
        self.dynCall_viiiifiifi = partial(self.instance.exports(self.store)["dynCall_viiiifiifi"], self.store)
        self.dynCall_viiiifiii = partial(self.instance.exports(self.store)["dynCall_viiiifiii"], self.store)
        self.dynCall_viiiifiiii = partial(self.instance.exports(self.store)["dynCall_viiiifiiii"], self.store)
        self.dynCall_viiiifiiiii = partial(self.instance.exports(self.store)["dynCall_viiiifiiiii"], self.store)
        self.dynCall_viiiifiiiiif = partial(self.instance.exports(self.store)["dynCall_viiiifiiiiif"], self.store)
        self.dynCall_viiiifiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiifiiiiiiii"], self.store)
        self.dynCall_viiiii = partial(self.instance.exports(self.store)["dynCall_viiiii"], self.store)
        self.dynCall_viiiiif = partial(self.instance.exports(self.store)["dynCall_viiiiif"], self.store)
        self.dynCall_viiiiiffi = partial(self.instance.exports(self.store)["dynCall_viiiiiffi"], self.store)
        self.dynCall_viiiiiffii = partial(self.instance.exports(self.store)["dynCall_viiiiiffii"], self.store)
        self.dynCall_viiiiifi = partial(self.instance.exports(self.store)["dynCall_viiiiifi"], self.store)
        self.dynCall_viiiiifiii = partial(self.instance.exports(self.store)["dynCall_viiiiifiii"], self.store)
        self.dynCall_viiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiii"], self.store)
        self.dynCall_viiiiiif = partial(self.instance.exports(self.store)["dynCall_viiiiiif"], self.store)
        self.dynCall_viiiiiifddfiii = partial(self.instance.exports(self.store)["dynCall_viiiiiifddfiii"], self.store)
        self.dynCall_viiiiiiffffiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiffffiii"], self.store)
        self.dynCall_viiiiiifiifiii = partial(self.instance.exports(self.store)["dynCall_viiiiiifiifiii"], self.store)
        self.dynCall_viiiiiifjjfiii = partial(self.instance.exports(self.store)["dynCall_viiiiiifjjfiii"], self.store)
        self.dynCall_viiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiii"], self.store)
        self.dynCall_viiiiiiifddfii = partial(self.instance.exports(self.store)["dynCall_viiiiiiifddfii"], self.store)
        self.dynCall_viiiiiiiffffii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiffffii"], self.store)
        self.dynCall_viiiiiiifiifii = partial(self.instance.exports(self.store)["dynCall_viiiiiiifiifii"], self.store)
        self.dynCall_viiiiiiifjjfii = partial(self.instance.exports(self.store)["dynCall_viiiiiiifjjfii"], self.store)
        self.dynCall_viiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiii"], self.store)
        self.dynCall_viiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiifii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiifii"], self.store)
        self.dynCall_viiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiji = partial(self.instance.exports(self.store)["dynCall_viiiiiji"], self.store)
        self.dynCall_viiiij = partial(self.instance.exports(self.store)["dynCall_viiiij"], self.store)
        self.dynCall_viiiijii = partial(self.instance.exports(self.store)["dynCall_viiiijii"], self.store)
        self.dynCall_viiiijiiii = partial(self.instance.exports(self.store)["dynCall_viiiijiiii"], self.store)
        self.dynCall_viiij = partial(self.instance.exports(self.store)["dynCall_viiij"], self.store)
        self.dynCall_viiiji = partial(self.instance.exports(self.store)["dynCall_viiiji"], self.store)
        self.dynCall_viiijji = partial(self.instance.exports(self.store)["dynCall_viiijji"], self.store)
        self.dynCall_viij = partial(self.instance.exports(self.store)["dynCall_viij"], self.store)
        self.dynCall_viiji = partial(self.instance.exports(self.store)["dynCall_viiji"], self.store)
        self.dynCall_viijii = partial(self.instance.exports(self.store)["dynCall_viijii"], self.store)
        self.dynCall_viijiii = partial(self.instance.exports(self.store)["dynCall_viijiii"], self.store)
        self.dynCall_viijiijiii = partial(self.instance.exports(self.store)["dynCall_viijiijiii"], self.store)
        self.dynCall_viijijii = partial(self.instance.exports(self.store)["dynCall_viijijii"], self.store)
        self.dynCall_viijijiii = partial(self.instance.exports(self.store)["dynCall_viijijiii"], self.store)
        self.dynCall_viijijj = partial(self.instance.exports(self.store)["dynCall_viijijj"], self.store)
        self.dynCall_viijj = partial(self.instance.exports(self.store)["dynCall_viijj"], self.store)
        self.dynCall_viijji = partial(self.instance.exports(self.store)["dynCall_viijji"], self.store)
        self.dynCall_viijjii = partial(self.instance.exports(self.store)["dynCall_viijjii"], self.store)
        self.dynCall_viijjiii = partial(self.instance.exports(self.store)["dynCall_viijjiii"], self.store)
        self.dynCall_viijjji = partial(self.instance.exports(self.store)["dynCall_viijjji"], self.store)
        self.dynCall_vij = partial(self.instance.exports(self.store)["dynCall_vij"], self.store)
        self.dynCall_viji = partial(self.instance.exports(self.store)["dynCall_viji"], self.store)
        self.dynCall_vijii = partial(self.instance.exports(self.store)["dynCall_vijii"], self.store)
        self.dynCall_vijiii = partial(self.instance.exports(self.store)["dynCall_vijiii"], self.store)
        self.dynCall_vijiiii = partial(self.instance.exports(self.store)["dynCall_vijiiii"], self.store)
        self.dynCall_vijiji = partial(self.instance.exports(self.store)["dynCall_vijiji"], self.store)
        self.dynCall_vijijji = partial(self.instance.exports(self.store)["dynCall_vijijji"], self.store)
        self.dynCall_vijji = partial(self.instance.exports(self.store)["dynCall_vijji"], self.store)
        self.dynCall_vijjii = partial(self.instance.exports(self.store)["dynCall_vijjii"], self.store)
        self.dynCall_vijjji = partial(self.instance.exports(self.store)["dynCall_vijjji"], self.store)
        self.dynCall_vji = partial(self.instance.exports(self.store)["dynCall_vji"], self.store)
        self.dynCall_vjii = partial(self.instance.exports(self.store)["dynCall_vjii"], self.store)
        self.dynCall_vjiiii = partial(self.instance.exports(self.store)["dynCall_vjiiii"], self.store)
        self.dynCall_vjji = partial(self.instance.exports(self.store)["dynCall_vjji"], self.store)
        self.establishStackSpace = partial(self.instance.exports(self.store)["establishStackSpace"], self.store)
        self.getTempRet0 = partial(self.instance.exports(self.store)["getTempRet0"], self.store)
        self.runPostSets = partial(self.instance.exports(self.store)["runPostSets"], self.store)
        self.setTempRet0 = partial(self.instance.exports(self.store)["setTempRet0"], self.store)
        self.setThrew = partial(self.instance.exports(self.store)["setThrew"], self.store)
        self.stackAlloc = partial(self.instance.exports(self.store)["stackAlloc"], self.store)
        self.stackRestore = partial(self.instance.exports(self.store)["stackRestore"], self.store)
        self.stackSave = partial(self.instance.exports(self.store)["stackSave"], self.store)
        self.part1 = partial(self.instance.exports(self.store)["part1"], self.store)
